import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuration Google Sheets
def connection_google_sheets(json_keyfile, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(credentials)
    sheet = client.open(sheet_name).sheet1
    return sheet

def sauvegarder_donnees_google(sheet, data):
    sheet.append_row(data)

# Connexion à la Google Sheet
try:
    sheet = connection_google_sheets('credentials.json', 'Donnees_Patients')
except Exception as e:
    sheet = None
    st.error(f"Erreur de connexion à Google Sheets : {e}")

st.title('Besoin nutritionnel du patient 🍏')

# Fonctions utilitaires
def IMC(masse_actuelle, taille):
    return round(masse_actuelle / taille**2, 1)

def perte_de_masse(masse_avant, masse_actuelle):
    return round(((masse_avant - masse_actuelle) / masse_avant) * 100, 1)

# Formulaire de saisie
with st.form('Données'):
    masse_actuelle = st.number_input('Quel est le poids actuel du patient en kg ?')
    masse_avant = st.number_input('Quel était le poids à la dernière pesée du patient en kg ?')
    temps = st.number_input('Quelle durée sépare les deux pesées en mois ?', min_value=0)
    taille = st.number_input('Quelle est la taille du patient en m ?', min_value=0.5, max_value=2.5)
    eg = st.radio('Quel est l’état général du patient ?', options=['Bon', 'Mauvais'], index=0)
    age = st.number_input('Quel âge a le patient ?', min_value=0)
    ingesta = st.slider('Quels sont les ingestas du patient (100% = rien ne change d’habitude) ?', min_value=0, max_value=100, value=100)
    stress_metabolique = st.selectbox(
        'Quels facteurs de stress métaboliques affectent le patient ?',
        ('patient faible mais non allité ou maladie chronique avec complication', 'maladie active ou patient allité', 'patient de soins intensifs ou ventilation assistée')
    )
    alcool = st.radio('Le patient a-t-il des antécédents avec l’alcool ?', options=['Oui', 'Non'])
    hypo = st.radio('Le patient souffre-t-il d’hypophosphatémie, hypokaliémie ou hypomagnésémie ?', options=['Oui', 'Non'])
    type_patient = st.selectbox(
        'Le patient est ...',
        ('hospitalisé', 'en oncologie médicale', 'âgé dénutris', 'en neurologie type SLA', 'en péri-opératoire', 'en réanimation phase aiguë', 'réanimation phase anabolique')
    )
    submitted = st.form_submit_button('Soumettre')

if submitted:
    # Calculs de base
    imc = IMC(masse_actuelle, taille)
    perte = perte_de_masse(masse_avant, masse_actuelle)

    # Évaluation du poids ajusté pour les besoins caloriques
    if imc >= 30:
        PCI = 25 * (taille ** 2)
        PA = PCI + 0.25 * (masse_actuelle - PCI)
        poids_calcul = PA
    else:
        poids_calcul = masse_actuelle

    # Détection du risque de SRI
    def sri(imc, perte, temps, ingesta, hypo, alcool):
        criteres_majeurs = (
            imc < 16,
            perte >= 15 and temps <= 6,
            ingesta < 10 and temps <= 0.33,
            hypo == 'Oui'
        )
        criteres_mineurs = [
            16 <= imc < 18.5,
            perte >= 10 and 3 <= temps <= 6,
            ingesta == 0 and temps <= 0.17,
            alcool == 'Oui'
        ]
        risque_crit_majeur = any(criteres_majeurs)
        nb_criteres_mineurs = sum(criteres_mineurs)
        if risque_crit_majeur:
            return "Risque élevé (Critère majeur détecté)"
        elif nb_criteres_mineurs >= 2:
            return "Risque élevé (≥ 2 critères mineurs détectés)"
        else:
            return 'Pas de risque de SRI'

    risque_sri = sri(imc, perte, temps, ingesta, hypo, alcool)

    # Définition des besoins nutritionnels
    besoins = {
        'hospitalisé': (20, 35),
        'en oncologie médicale': (30, 35),
        'âgé dénutris': (30, 40),
        'en neurologie type SLA': (35, 35),
        'en péri-opératoire': (25, 30),
        'en réanimation phase aiguë': (20, 25),
        'réanimation phase anabolique': (25, 30)
    }
    besoins_proteines = {
        'hospitalisé': (1.0, 2.0),
        'en oncologie médicale': (1.2, 1.5),
        'âgé dénutris': (1.2, 1.5),
        'en neurologie type SLA': (1.2, 1.5),
        'en péri-opératoire': (1.2, 1.5),
        'en réanimation phase aiguë': (1.2, 1.5),
        'réanimation phase anabolique': (2.0, 2.0) if imc >= 30 else (1.2, 1.5)
    }

    # Calcul des besoins
    bgk, bdk = besoins.get(type_patient, (20, 25))
    kcal_min = poids_calcul * bgk
    kcal_max = poids_calcul * bdk

    bgp, bdp = besoins_proteines.get(type_patient, (1.2, 1.5))
    prot_min = poids_calcul * bgp
    prot_max = poids_calcul * bdp

    # Affichage des résultats
    st.write(f"IMC du patient : **{imc}**")
    st.write(f"Perte de poids : **{perte}%**")
    st.write(f"Les besoins caloriques sont de **{round(kcal_min, 1)} kcal/j** à **{round(kcal_max, 1)} kcal/j**.")
    st.write(f"Les besoins en protéines sont de **{round(prot_min, 1)} g/j** à **{round(prot_max, 1)} g/j**.")
    st.write(f"Risque de syndrome de renutrition inappropriée (SRI) : **{risque_sri}**")

    # Sauvegarde dans Google Sheets
    if sheet:
        try:
            sauvegarder_donnees_google(sheet, [
                masse_actuelle, masse_avant, temps, taille, eg, age, ingesta, stress_metabolique, alcool, hypo,
                type_patient, imc, perte, round(kcal_min, 1), round(kcal_max, 1), round(prot_min, 1), round(prot_max, 1)
            ])
            st.success("Données sauvegardées avec succès dans Google Sheets !")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde des données : {e}")

