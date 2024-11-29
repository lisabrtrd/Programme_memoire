import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Autorisations d'accès à Google Sheets et Google Drive
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = {
  "type": "service_account",
  "project_id": "memoire-443220",
  "private_key_id": "167f4fcac86e9f822cf033f046b04d9fc361b0d9",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsB2rO67VNWSQl\n0aleb3+BpJfA7F9ZogKAdkP+CcGRZr58bUltMmzMdM3Cm7DCs+tMOEPCPGmwgCbR\nz434+gTiWhH5vPpdVPBRDTt/zpGMV1qYTyYpVnN9Qh8ncWwmb7WbgqrS3f+FnlCK\nE60hiJdVc+N1F2+cgghX4L+xc3OEzDDGuzBDQGWjtn8TIDdnOxV15NJ3d9qy/Cpg\naTjZ3Dmn8iUBLvazRZ+L9EqpLu3mKSFi2yegcTbzYXB4H02RUSauEVF7JiXCea20\nO+BG3HffroxldS/q1NXqgGGoj0SDwxMR1i4eltxXIgV9A9wkWQ7NHdbTctEtqRd4\nblTlSP9BAgMBAAECggEAUAGNF5oA8m2sRZh6VCy32MQDPdrQx5902WjnW00PRL/L\nhJPRK+NhPT9veHwvG4ZQvtyGCt5M6yTWqQqGBU7GGb15EbRlniWENLXaP6kDAQmZ\nXS+mWGBYCt/HHHGAMmoOxLnjF3nevjZwT58yDF/5vejNVuYk5t2E4tXoYS+IALCv\nNp0qpig3ew81y8aU/Xr75AF3l7/3ae+uxJ9PVJHQ+mNqZLtRkakkggUOoKbSpiG2\nNij6rFIqPRdk1lyZ69SUdxAejYp73g3lsY/uaRaVnks9TGGptuTXtXhkqkX+O4NA\n/IQNFZ9XERrrGppVqSJq5ICGKjS9qDsbvKUTsY+ClwKBgQDxi03ITK9CsuwuNeEG\n7LDnu1nD+MYHz2BF7yv1Vl/CLiA8amwx1GNMsEvHyPC20wq454rxLlMR4Db+Wnk+\n2Ly1JTnXg26+kThJAipb7K7gSyVUqZuZxpmHOO0iuoOyBu7LcC4YbyBJv8uUSyTd\n3KSPYLz6fS2PDt5BXUoUCIUaWwKBgQC2UxJiCxQht1jqs7oahMuWbXdIyoif+G8F\n0EUnsmTUzge0395v8phPOm/s4zIa9pv3qGb4rjkVmxU68s4wruzTGfGSSS3J/IHH\nVsk9Jyy3hM5C+qmwnFvw8dGmYDZx//kCT8CnyClMpwTVuj5NzYxO0YmlL8hSsA54\nZB1M3zUnkwKBgBM3gAK1hyQJVB0BEFwarKBjGWsr+aVZbFFkC91C9+9c+BeWZ/E2\n8oeBZyYH6I7DD5FSao1xoA5GBloKHKdRWwIWahmpTUBAEXhNgc06cVdK4zdvHwAG\n+uP1NXiT2jJptsncrO4ouSrk5W9w4wf7q+P0UFSlbOB60Ffm8iPR4bUNAoGBAIwM\nkZFYGzWu5ZEbTzfxi4TYPwld8caXiYh4q7ZLdOJ2BDtuvylUuqQZKkJXXnSRu8pn\nw/j/sv+iqZMnUTTaGTYqtoH8zjxaRsH9KwVbYyDw1ZNjghcUdBdHWRgozYmR6w9Y\nfY8j1H15yd/2eMdAvacJk2acpo7Fh8f4dv1Gc0kbAoGAMYW8p1050MMXIhDIXLHl\nX5//0kD6gSumUbnAO2AK8jlLtQ7F8lPh+DSKR1Yuv98qjzPEQNOZNZkoFTijW6Wh\ngOGyTRC5lGrm2shuqVVD/btRP9P7la+oPczZius66aXIhywPIMBPamcJgDCFff2U\nyYJu02PD70XS2PkOlAesH2k=\n-----END PRIVATE KEY-----\n",
  "client_email": "lb-151@memoire-443220.iam.gserviceaccount.com",
  "client_id": "115119367613138427301",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lb-151%40memoire-443220.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
client = gspread.authorize(creds)

# Ouvrir la feuille Google Sheets (remplacez par le nom de votre fichier Google Sheets)
spreadsheet = client.open("Donnees_patients")  # Remplacez par le nom exact de votre Google Sheets
worksheet = spreadsheet.get_worksheet(0)  # Accéder à la première feuille

# Interface utilisateur de Streamlit
st.title('Saisie des données pour analyse nutritionnelle')

with st.form('Données'):
    # Entrée des données utilisateur
    masse_actuelle = st.number_input('Quel est le poids actuel du patient en kg ?', min_value=0.0, step=0.1)
    masse_avant = st.number_input('Quel était le poids à la dernière pesée du patient en kg ?', min_value=0.0, step=0.1)
    taille = st.number_input('Quelle est la taille du patient en m ?', min_value=0.0, step=0.01)
    age = st.number_input('Quel âge a le patient ?', min_value=0, step=1)
    eg = st.radio('Quel est l’état général du patient ?', options=['Bon', 'Mauvais'], index=0)
    ingesta = st.slider('Quels sont les ingestas du patient sachant 100% = rien ne change de d habitude ?', min_value=0, max_value=100, value=100)
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
    
    # Soumettre les données
    submitted = st.form_submit_button('Soumettre')

# Lorsque l'utilisateur soumet le formulaire, le programme calcule et enregistre les données
if submitted:
    # Calcul de l'IMC
    imc = round(masse_actuelle / taille ** 2, 2)

    # Calcul de la perte de poids
    perte = round(((masse_avant - masse_actuelle) / masse_avant) * 100, 2)

    # Ajouter les données dans Google Sheets
    worksheet.append_row([
        masse_actuelle,
        masse_avant,
        perte,
        age,
        taille,
        eg,
        ingesta,
        stress_metabolique,
        alcool,
        hypo,
        type_patient,
        imc
    ])

    # Affichage des résultats sur Streamlit
    st.write(f"Les données ont été enregistrées avec succès dans Google Sheets !")
    st.write(f"IMC du patient : {imc}")
    st.write(f"Perte de poids : {perte}%")

    # Ajoutez des calculs supplémentaires si nécessaire (par exemple, besoins caloriques et en protéines)
    st.write("Calcul des besoins nutritionnels :")

    # Calcul des besoins nutritionnels basés sur le type de patient
    besoins = {
        'hospitalisé': (20, 35),
        'en oncologie médicale': (30, 35),
        'âgés dénutris': (30, 40),
        'en neurologie type SLA': (35, 35),
        'en péri-opératoire': (25, 30),
        'en réanimation phase aiguë': (20, 25),
        'réanimation phase anabolique': (25, 30)
    }
    bgk, bdk = besoins.get(type_patient, (20, 25))  # Utilise une valeur par défaut si type_patient est inconnu
    facteur_ingesta = (1 - ingesta / 100)  # Facteur d'ajustement en fonction des ingestas

    kcal_min = masse_actuelle * bgk * facteur_ingesta
    kcal_max = masse_actuelle * bdk * facteur_ingesta
    bgp = masse_actuelle * 1.2 * facteur_ingesta
    bdp = masse_actuelle * 1.5 * facteur_ingesta

    st.write(f"Les besoins caloriques sont de **{round(kcal_min, 1)} kcal/j** à **{round(kcal_max, 1)} kcal/j**.")
    st.write(f"Les besoins en protéines sont de **{round(bgp, 1)} g/j** à **{round(bdp, 1)} g/j**.")



