from dico import capteurs
import streamlit as st
from fonctions_de_chargement import initialisation_tab
from fonctions_de_chargement import envoyer_dataframe
from superbase import  create_client



df_historique_total= initialisation_tab(capteurs) #récupération de l'historique

#####################connexion avec la BD###############################
url = "https://wynjcciiprpxtkvjaurm.supabase.co"
key = st.secrets["supabase_tok"]

supabase = create_client(url, key)
supabase.rpc("vider_mesures").execute()#vider les données de la BD
print("Table mesures vidée")

###############################envoie vers la BD "mesures" ##############################################

test = supabase.table("mesures").select("*").limit(1).execute()###
print(test.data)################################################## teste la connexion à la BD

envoyer_dataframe(df_historique_total,"mesure", batch_size=1000) 