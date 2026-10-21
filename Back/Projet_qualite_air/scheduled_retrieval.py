# Scheduled Retrieval (30min)

import logging
import os
import sys
from dico import capteurs
from fonctions_de_chargement import envoyer_dataframe, initialisation_tab
from supabase import create_client

# Logs config
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", encoding="utf-8")
logger = logging.getLogger(__name__)

# .env settings
SUPABASE_TOKEN = os.getenv("SUPABASE_TOKEN", os.getenv("supabase_tok"))
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wynjcciiprpxtkvjaurm.supabase.co")


def retrieval() -> None:
  """Run data retrieval periodically and push to Supabase."""
  if not SUPABASE_TOKEN:
    logger.error("Missing required Supabase token environment variable.")
    sys.exit(1)

  try:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_TOKEN)

    # Fetch data
    update = initialisation_tab(capteurs, mode="current")

    # Validate data before sending
    if update is None or (hasattr(update, "empty") and update.empty):
      logger.warning("No data retrieved. Skipping upload.")
      return

    logger.info(f"Lignes récupérées : {len(update)}")

    # Send data
    envoyer_dataframe(supabase_client, update, "mesures", batch_size=34)
    logger.info("Synchronisation réussie avec Supabase.")

  except Exception as e:
    logger.exception("An error occurred during retrieval/upload: %s", e)
    # Exit with code 1 so GitHub Actions or your runner knows the job failed
    sys.exit(1)


if __name__ == "__main__":
  retrieval()