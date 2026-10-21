"""Configuration centralisée de l'API Smart City.

Les valeurs sont lues depuis les variables d'environnement (ou Back/api/.env).
Le token Supabase retombe sur Back/secrets.toml pour rester compatible avec
les scripts existants de l'équipe data.
"""
from __future__ import annotations

import os
import secrets
import tomllib
from pathlib import Path

from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parent
BACK_DIR = API_DIR.parent
PREDICTION_DIR = BACK_DIR / "prediction"

load_dotenv(API_DIR / ".env")


def _secret_from_toml(key: str) -> str | None:
    for path in (BACK_DIR / "secrets.toml", PREDICTION_DIR / ".streamlit" / "secrets.toml"):
        if path.exists():
            try:
                with path.open("rb") as fh:
                    value = tomllib.load(fh).get(key)
                if value:
                    return value
            except (OSError, tomllib.TOMLDecodeError):
                continue
    return None


# ── Supabase ────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wynjcciiprpxtkvjaurm.supabase.co").rstrip("/")
SUPABASE_TOKEN = (
    os.getenv("SUPABASE_TOKEN")
    or os.getenv("supabase_tok")
    or _secret_from_toml("supabase_tok")
)
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "mesures")

# ── Sécurité ────────────────────────────────────────────────────────────────
# En production, définir JWT_SECRET : sinon les tokens sont invalidés à chaque redémarrage.
JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_urlsafe(48)
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "8"))
CORS_ORIGINS = [o.strip() for o in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if o.strip()]

# ── Cache (secondes) ────────────────────────────────────────────────────────
CACHE_TTL_MEASURES = int(os.getenv("CACHE_TTL_MEASURES", "120"))
CACHE_TTL_PREDICTIONS = int(os.getenv("CACHE_TTL_PREDICTIONS", "1800"))

# ── Modèle IA ───────────────────────────────────────────────────────────────
MODEL_PATH = Path(os.getenv("MODEL_PATH", PREDICTION_DIR / "modele_aqi" / "bundle_aqi.joblib"))

# ── Alertes e-mail (optionnel, US-015) ──────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", SMTP_USER or "")
ALERT_EMAIL_TO = [e.strip() for e in os.getenv("ALERT_EMAIL_TO", "").split(",") if e.strip()]

# ── Power BI Embedded / Service ─────────────────────────────────────────────
POWERBI_TENANT_ID = os.getenv("POWERBI_TENANT_ID", "organizations")
POWERBI_CLIENT_ID = os.getenv("POWERBI_CLIENT_ID", "ea0616ba-638b-4df5-95b9-636659ae5121")
POWERBI_CLIENT_SECRET = os.getenv("POWERBI_CLIENT_SECRET")
POWERBI_WORKSPACE_ID = os.getenv("POWERBI_WORKSPACE_ID")
POWERBI_REPORT_ID = os.getenv("POWERBI_REPORT_ID", "70b30346-6b29-4afa-8814-d5d0d3cdb88f")
POWERBI_USERNAME = os.getenv("POWERBI_USERNAME", "ngulrich@etudiant-esic.fr")
POWERBI_PASSWORD = os.getenv("POWERBI_PASSWORD", "Lamuchanho5")

# ── Logs & Réseau ───────────────────────────────────────────────────────────
LOG_DIR = Path(os.getenv("LOG_DIR", API_DIR / "logs"))
SSL_VERIFY = os.getenv("SSL_VERIFY", "false").lower() in ("1", "true", "yes")

