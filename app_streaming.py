
#supabase.rpc("vider_mesures").execute()
import time as time_mod #pour éviter le conflit avec "time" qui est ma variable temporelle
from dico import capteurs
from fonctions_de_chargement import initialisation_tab
from fonctions_de_chargement import envoyer_dataframe
from supabase import  create_client
import os, sys
from dotenv import load_dotenv

import logging






base = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
############################################Afficher les logs###################################
logging.basicConfig(
    filename=os.path.join(base, "log.txt"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    encoding="utf-8"
)
logging.getLogger("httpx").setLevel(logging.WARNING)
############################################################################################
load_dotenv(os.path.join(base, ".env"))

#####################connexion avec la BD###############################
url = "https://wynjcciiprpxtkvjaurm.supabase.co"

SUPABASE_TOKEN = os.getenv("SUPABASE_TOKEN", os.getenv("supabase_tok"))

# key = os.environ["SUPABASE_TOK"]
key = os.environ["SUPABASE_TOKEN"]
supabase = create_client(url, key)


#supabase.rpc("vider_mesures").execute()
import time as time_mod #pour éviter le conflit avec "time" qui est ma variable temporelle
# while True:
try:

    mise_a_jour = initialisation_tab(
        capteurs,
        mode="current"
    )

    logging.info(f"Lignes récupérées : {len(mise_a_jour)}")

    envoyer_dataframe(
        supabase,
        mise_a_jour,
        "mesures",
        batch_size = 34
    )
except Exception as e:
    print("Erreur :", e)
logging.info("prochaine récupération dans 30 min")

    # time_mod.sleep(1800)


