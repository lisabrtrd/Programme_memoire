import streamlit as st

st.title('Besoin nutritionnel du patient🍏')

def IMC(masse_actuelle, taille):
    return round(masse_actuelle / taille**2, 2)

def perte_de_masse(masse_avant, masse_actuelle):
    return round(((masse_avant - masse_actuelle) / masse_avant) * 100, 2)

################# DONNEES #####################
with st.form('Données'):
    masse_actuelle = st.number_input('Quel est le poids actuel du patient en kg ?')
    masse_avant = st.number_input('Quel était le poids habituel du patient en kg ?')
    temps = st.number_input('Quelle durée sépare les deux pesées en mois ?')
    taille = st.number_input('Quelle est la taille du patient en m ?')
    eg = st.radio('Quel est l’état général du patient ?', options=['Bon', 'Mauvais'], index=0)
    age = st.number_input('Quel âge a le patient ?')
    ingesta = st.slider('Quels sont les prises alimentaires actuelles du patient sachant 100% = rien ne change de d habitude ?', min_value=0, max_value=100, value=100)
    stress_metabolique = st.selectbox(
        'Quels facteurs de stress métaboliques affectent le patient ?',
        ('patient faible mais non allité ou maladie chronique avec complication', 
         'maladie active ou patient allité', 
         'patient de soins intensifs ou ventilation assistée'))
    alcool = st.radio('Le patient a-t-il des antécédents avec l’alcool ?', options=['Oui', 'Non'])
    hypo = st.radio('Le patient souffre-t-il d’hypophosphatémie, hypokaliémie ou hypomagnésémie ?', options=['Oui', 'Non'])
    type_patient = st.selectbox(
        'Le patient est ...',
        ('hospitalisé', 'en oncologie médicale', 'âgé dénutris', 'en neurologie type SLA', 
         'en péri-opératoire', 'en réanimation phase aiguë', 'réanimation phase anabolique'))
    data = {
    "Marque": ["Fortimel", "Fortimel", "Fresubin", "Fresubin", "Delical", "Delical", "Clinutren", "Clinutren"],
    "Produit": [
        "Fortimel Compact Protein", "Fortimel Jucy",
        "Fresubin PRO Drink", "Fresubin Energy Drink",
        "Delical HPHC Concentré", "Delical Saveurs Fruitées",
        "Clinutren Boisson 2kcal", "Clinutren Dessert 2kcal"
    ],
    "Contenance": ["125 ml", "200 ml", "125 ml", "200 ml", "200 ml", "200 ml", "200 ml", "125 g"],
    "Kcal": [300, 300, 400, 300, 452, 260, 400, 250],
    "Protéines (g)": [18, 8, 20, 12, 29, 8, 20, 12.5]
}

df = pd.DataFrame(data)

# Interface utilisateur
st.title("Sélection des Compléments Nutritionnels Oraux (CNO)")

# Sélection des marques (seulement Fortimel, Delical, Fresubin, Clinutren)
marques_autorisees = ["Fortimel", "Fresubin", "Delical", "Clinutren"]
marques_selectionnees = st.multiselect("Sélectionnez les marques disponibles :", options=marques_autorisees)

# Filtrer et afficher les résultats
if marques_selectionnees:
    resultats = df[df["Marque"].isin(marques_selectionnees)]
    st.write("Produits correspondants :")
    st.dataframe(resultats, hide_index=True)
else:
    st.write("Veuillez sélectionner au moins une marque.")
    
    submitted = st.form_submit_button('Soumettre')

############## calcul de base ###########################
if submitted:
    st.write('IMC du patient est de', IMC(masse_actuelle, taille))
    st.write('La perte de poids est de', perte_de_masse(masse_avant, masse_actuelle), '%')
    imc = IMC(masse_actuelle, taille)
    
    # Poids ajusté pour les besoins caloriques
    if imc >= 30:
        PCI = 25 * (taille ** 2)
        PA = PCI + 0.25 * (masse_actuelle - PCI)
        st.write(f"Poids ajusté (PA) : **{round(PA, 1)} kg**")
    else:
        PA = masse_actuelle

    # état de dénutrition
    perte = perte_de_masse(masse_avant, masse_actuelle)
    etat_dénutrition = 'patient normal'
    if perte >= 15 and 1<= temps <= 6:
        etat_dénutrition = "dénutrition sévère"
    elif perte >= 10 and temps <= 1:
        etat_dénutrition = "dénutrition sévère"
    elif perte >= 10 and 1<= temps <= 6:
        etat_dénutrition = "dénutrition modérée"
    elif perte >= 5 and temps <= 1:
        etat_dénutrition = "dénutrition modérée"

    st.write(f"L'état de dénutrition du patient : **{etat_dénutrition}**")

        # Score nutritionnel NRS
    score_nut = []
    if imc > 20.5:
        score_nut.append(0)
    elif 18.5 < imc < 20.5 and eg == 'Bon':
        score_nut.append(1)
    elif 18.5 < imc < 20.5 and eg == 'Mauvais':
        score_nut.append(2)
    elif imc < 18.5 and eg == 'Mauvais':
        score_nut.append(3)

    if perte == 0:
        score_nut.append(0)
    elif perte > 5 and 2 < temps <= 3:
        score_nut.append(1)
    elif perte > 5 and 1 < temps <= 2:
        score_nut.append(2)
    elif perte > 5 and 0 < temps <= 1:
        score_nut.append(3)

    if ingesta > 75:
        score_nut.append(0)
    elif 50 < ingesta < 75:
        score_nut.append(1)
    elif 25 < ingesta < 50:
        score_nut.append(2)
    elif ingesta < 25:
        score_nut.append(3)

    score_nutritionnel = max(score_nut)

    # Score de maladie
    score_maladie = 0
    if 'maladie chronique avec complication' in stress_metabolique:
        score_maladie = 1
    elif 'maladie active' in stress_metabolique or 'patient allité' in stress_metabolique:
        score_maladie = 2
    elif 'patient de soins intensifs' in stress_metabolique or 'ventilation assistée' in stress_metabolique:
        score_maladie = 3

    # Calcul du score total
    score_total = score_nutritionnel + score_maladie
    if age >= 70:
        score_total += 1

    st.write(f"Score nutritionnel total ajusté à l'âge : **{score_total}**")

    # Besoins énergétiques et protéiques selon type de patient
    besoins = {
        'hospitalisé': (20, 35),
        'en oncologie médicale': (30, 35),
        'âgés dénutris': (30, 40),
        'en neurologie type SLA': (35, 35),
        'en péri-opératoire': (25, 30),
        'en réanimation phase aiguë': (20, 25),
        'réanimation phase anabolique': (25, 30)
    }
    
    besoins_proteines = {
        'hospitalisé': (1.0, 2.0),
        'en oncologie médicale': (1.2, 1.5),
        'âgés dénutris': (1.2, 1.5),
        'en neurologie type SLA': (1.5, 1.5),
        'en péri-opératoire': (1.2, 1.5),
        'en réanimation phase aiguë': (1.2, 1.5),
        'réanimation phase anabolique': (2.0, 2.5) if imc >= 30 else (1.2, 1.5)
    }

    bgk, bdk = besoins.get(type_patient, (20, 25))  # Besoins énergétiques
    bgp_proteines, bdp_proteines = besoins_proteines.get(type_patient, (1.2, 1.5))  # Besoins en protéines

    # Calcul du facteur d'ingesta
    facteur_ingesta = (1 - ingesta / 100)

    # Évaluation du risque de SRI
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

    if risque_sri != 'Pas de risque de SRI':  # N'affiche que si un risque est détecté
        st.write(f"Évaluation du risque de SRI : **{risque_sri}**")
        if risque_sri in ["Risque élevé (Critère majeur détecté)", "Risque élevé (≥ 2 critères mineurs détectés)"]:
            st.warning("Restriction calorique appliquée à 500 kcal/j en raison du risque de SRI. Renvoyer vers un professionnel")
            kcal_min, kcal_max = 500, 500
            bgp, bdp = None, None
            with st.expander("ℹ️ En savoir plus sur le SRI"):
                st.write("Le syndrome de renutrition inappropriée (SRI) survient lorsqu’un patient dénutri ou ayant subi un jeûne prolongé reçoit un apport trop rapide et excessif en calories et micronutriments. Ce syndrome peut être fatal en raison des déséquilibres électrolytiques qu’il provoque, pouvant conduire à une défaillance multiviscérale. Il est donc essentiel de le détecter précocement. Les principales manifestations cliniques du SRI incluent : hypertension artérielle, œdèmes, insuffisance cardiaque transitoire, ainsi que d'autres complications métaboliques graves.")
    else:
        kcal_min = PA * bgk * facteur_ingesta
        kcal_max = PA * bdk * facteur_ingesta
        bgp = PA * bgp_proteines * facteur_ingesta
        bdp = PA * bdp_proteines * facteur_ingesta

        st.write(f"Les besoins caloriques sont de **{round(kcal_min, 1)} kcal/j** à **{round(kcal_max, 1)} kcal/j**.")
        st.write(f"Les besoins en protéines sont de **{round(bgp, 1)} g/j** à **{round(bdp, 1)} g/j**.")
        st.warning ("Ne pas dépasser les 600kcal/j de CNO ! Si c'est le cas, pensez à orienter le patient vers un nutritionniste et peut-être commencer à amener l'idée de la nutrition entérale selon le problème du patient")



