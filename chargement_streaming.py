
#supabase.rpc("vider_mesures").execute()
import time as time_mod #pour éviter le conflit avec "time" qui est ma variable temporelle
from dico import capteurs
import streamlit as st
from fonctions_de_chargement import initialisation_tab
from fonctions_de_chargement import envoyer_dataframe
from superbase import  create_client



#####################connexion avec la BD###############################
url = "https://wynjcciiprpxtkvjaurm.supabase.co"
key = st.secrets["supabase_tok"]
supabase = create_client(url, key)


#supabase.rpc("vider_mesures").execute()
import time as time_mod #pour éviter le conflit avec "time" qui est ma variable temporelle
while True:
    try:

        mise_a_jour = initialisation_tab(
            capteurs,
            mode="current"
        )

        print("Lignes récupérées :", len(mise_a_jour))

        envoyer_dataframe(
            mise_a_jour,
            "mesures",
            batch_size = 34
        )
    except Exception as e:
        print("Erreur :", e)
    print("prochaine récupération dans 30 min")

    time_mod.sleep(1200)


