import streamlit as st

st.title ('Besoin nutritionnel du patient🍏')


def IMC(masse_actuelle, taille):
    return round(masse_actuelle / taille**2)

def perte_de_masse(masse_avant, masse_actuelle):
    return round(((masse_avant - masse_actuelle) / masse_avant) * 100)

def evaluer_sri(imc, perte, temps, ingesta, hypo, alcool):
    criteres_majeurs = (
        imc < 16,
        perte >= 15 and temps <= 6,
        ingesta > 10,
        hypo == 'Oui'
    )
    criteres_mineurs = [
        16 <= imc < 18.5,
        perte >= 10 and temps <= 6,
        ingesta > 50,
        alcool == 'Oui'
    ]

    is_critere_majeur = any(criteres_majeurs)
    nb_criteres_mineurs = sum(criteres_mineurs)

    if is_critere_majeur:
        return "Risque élevé"
    elif nb_criteres_mineurs >= 2:
        return "Risque élevé"
    else:
        return "Risque faible"


################# DONNEES #####################
with st.form ('Données'):
    masse_actuelle = st.number_input('Quel est le poids actuel du patient en kg ?')
    masse_avant = st.number_input('Quel était le poids à la dernière pesée du patient en kg ?')
    temps = st.number_input('Quelle durée sépare les deux pesées en mois ?')
    taille = st.number_input('Quelle est la taille du patient en m ?')
    eg = st.radio('Quel est l’état général du patient ?', options=['Bon', 'Mauvais'], index=0)
    age = st.number_input('Quel âge a le patient ?')
    ingesta = st.slider('Quels sont les ingestas du patient sachant 100% = rien ne change de d habitude ?', min_value=0, max_value=100, value=100)
    stress_metabolique = st.selectbox(
        'Quels facteurs de stress métaboliques affectent le patient ?',
        ('patient faible mais non allité ou maladie chronique avec complication' , 'maladie active ou patient allité' , 'patient de soins intensifs ou ventilation assistée'))
    alcool = st.radio('Le patient a-t-il des antécédents avec l’alcool ?', options=['Oui', 'Non'])
    hypo = st.radio('Le patient souffre-t-il d’hypophosphatémie, hypokaliémie ou hypomagnésémie ?', options=['Oui', 'Non'])
    type_patient = st.selectbox(
        'Le patient est ...',
        ('hospitalisé','en oncologie médicale','âgé dénutris','en neurologie type SLA', 'en péri-opératoire','en réanimation phase aigue','réanimation phase anabolique'))
    
    submitted = st.form_submit_button('Soumettre')

############## calcul de base ###########################
if submitted : 
     st.write('IMC du patient est de',IMC(masse_actuelle, taille))
     st.write('La perte de poids est de', perte_de_masse(masse_avant, masse_actuelle), '%')
     imc = IMC (masse_actuelle,taille)
     if imc >= 30 :
            PCI = 25 * (taille ** 2)
            PA = PCI + 0.25 * (masse_actuelle - PCI)
            masse_actuelle = PA
            st.write(f"Poids ajusté (PA) : **{round(PA, 1)} kg**")
    
    #etat de dénutrition#
     perte = perte_de_masse(masse_avant,masse_actuelle)
     if perte >= 15 and temps <= 6:
        etat_dénutrition = "dénutrition sévère"
     elif perte >= 10 and temps <= 1:
        etat_dénutrition = "dénutrition sévère"
     elif perte >= 10 and temps > 1:
        etat_dénutrition = "dénutrition modérée"
     elif perte >= 5 and temps <= 1:
        etat_dénutrition = "dénutrition modérée"
     else:
        etat_dénutrition = "patient normal"

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

    # Calcul du risque SRI
     risque_sri = evaluer_sri(imc, perte, temps, ingesta, hypo, alcool)
     st.write ( f"Évaluation du risque de SRI : **{risque_sri}**" )

    # Besoins nutritionnels
     besoins = {
        'hospitalisé': (20, 35),
        'en oncologie médicale': (30, 35),
        'âgés dénutris': (30, 40),
        'en neurologie type SLA': (35, 35),
        'en péri-opératoire': (25, 30),
        'en réanimation phase aigüe': (20, 25),
        'en réanimation phase anabolique': (25, 30)
    }

     bgk, bdk = besoins[type_patient]
     facteur_ingesta = (1 - ingesta / 100)

     if risque_sri == ["Risque élevé"]:
        kcal_min, kcal_max = 500, 500  # Restriction calorique à 500 kcal/j
        bgp, bdp = None, None  # Pas de calcul pour les protéines pour le moment
        st.warning("Restriction calorique appliquée à 500 kcal/j en raison du risque de SRI.")
     else:
        kcal_min = masse_actuelle * bgk * facteur_ingesta
        kcal_max = masse_actuelle * bdk * facteur_ingesta
        bgp = masse_actuelle * 1.2 * facteur_ingesta
        bdp = masse_actuelle * 1.5 * facteur_ingesta

        st.write(f"Le patient doit consommer entre **{round(kcal_min)}** et **{round(kcal_max)}** kcal/j")
        st.write(f"et entre **{round(bgp, 1)}** et **{round(bdp, 1)}** g de protéines/j")
