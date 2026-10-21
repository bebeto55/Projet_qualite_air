"""Alertes de dépassement de seuil (US-015) et recommandations citoyennes (US-016)."""
from __future__ import annotations

import json
import smtplib
import threading
from datetime import datetime
from email.message import EmailMessage

import pandas as pd

from data_service import PARIS, _iso, _num, latest_per_sensor
from logs_service import app_log
from settings import (ALERT_EMAIL_FROM, ALERT_EMAIL_TO, API_DIR, LOG_DIR,
                      SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER)

CONFIG_FILE = API_DIR / "alert_config.json"
OUTBOX_FILE = LOG_DIR / "emails_sent.json"
DEFAULT_CONFIG = {
    # Seuils du cahier des charges (µg/m³) + O3 / indice européen
    "thresholds": {"pm25": 50, "pm10": 80, "no2": 200, "o3": 100},
    "notifications": {"email": True, "sms": False},
    "recipients": ALERT_EMAIL_TO or ["marie.dubois@metropole.fr"],
}
COLUMNS = {"pm25": ("pm2_5", "PM2.5"), "pm10": ("pm10", "PM10"),
           "no2": ("nitrogen_dioxide", "NO2"), "o3": ("ozone", "O3")}

_lock = threading.Lock()
_acknowledged: set[str] = set()
_notified: set[str] = set()


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return {**DEFAULT_CONFIG, **cfg, "thresholds": {**DEFAULT_CONFIG["thresholds"], **cfg.get("thresholds", {})}}
        except (OSError, json.JSONDecodeError):
            app_log.warning("alert_config.json illisible, valeurs par défaut utilisées")
    return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(cfg: dict) -> dict:
    with _lock:
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    return cfg


def build_alerts(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    cfg = load_config()
    alerts = []
    for row in latest_per_sensor(df).to_dict("records"):
        for key, (col, label) in COLUMNS.items():
            val, thr = row.get(col), cfg["thresholds"].get(key)
            if thr is None or val is None or pd.isna(val) or val <= thr:
                continue
            aid = f"{row['capteur_id']}-{key}-{row['time']:%Y%m%d%H}"
            if aid in _acknowledged:
                continue
            alerts.append({
                "id": aid, "type": "threshold", "sensorId": row["capteur_id"], "sensor": row["capteur_nom"],
                "pollutant": label, "value": _num(val), "threshold": thr,
                "level": "danger" if val > 1.5 * thr else "warning", "ts": _iso(row["time"]),
            })
    _notify(alerts, cfg)
    return alerts


def acknowledge(alert_id: str) -> None:
    _acknowledged.add(alert_id)


def _notify(alerts: list[dict], cfg: dict) -> None:
    new = [a for a in alerts if a["id"] not in _notified]
    if not new:
        return
    _notified.update(a["id"] for a in new)
    if not (cfg["notifications"].get("email") and cfg.get("recipients")):
        return
    threading.Thread(target=send_email, args=(new, cfg["recipients"]), daemon=True).start()


def get_sent_emails(limit: int = 20) -> list[dict]:
    if not OUTBOX_FILE.exists():
        return []
    try:
        items = json.loads(OUTBOX_FILE.read_text(encoding="utf-8"))
        return items[:limit]
    except Exception:
        return []


def _record_outbox(entry: dict) -> None:
    with _lock:
        existing = get_sent_emails(100)
        existing.insert(0, entry)
        OUTBOX_FILE.write_text(json.dumps(existing[:100], indent=2, ensure_ascii=False), encoding="utf-8")


def send_email(alerts: list[dict], recipients: list[str]) -> dict:
    """Envoie l'e-mail via SMTP si configuré, et l'archive dans la boîte d'envoi locale."""
    subject = f"[Smart City Île-de-France] {len(alerts)} alerte(s) qualité de l'air"
    sender = ALERT_EMAIL_FROM or "alertes@smartcity-idf.fr"
    lines = [f"- Station {a['sensor']} : {a['pollutant']} = {a['value']} µg/m³ (seuil : {a['threshold']} µg/m³)" for a in alerts]
    body = (
        "Bonjour,\n\n"
        "La plateforme Smart City Île-de-France a détecté le(s) dépassement(s) de seuil suivant(s) :\n\n"
        + "\n".join(lines)
        + "\n\nConsultez le tableau de bord temps réel : http://localhost:5173/alerts\n"
        "— Service Surveillance Qualité de l'Air"
    )

    delivery_mode = "outbox_local"
    if SMTP_HOST:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg.set_content(body)
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as s:
                s.starttls()
                if SMTP_USER:
                    s.login(SMTP_USER, SMTP_PASSWORD or "")
                s.send_message(msg)
            delivery_mode = "smtp"
            app_log.info("E-mail d'alerte envoyé via SMTP à %s", recipients)
        except (smtplib.SMTPException, OSError) as exc:
            app_log.warning("SMTP indisponible (%s), archivage dans la boîte d'envoi locale", exc)

    entry = {
        "id": f"mail-{int(datetime.now(PARIS).timestamp() * 1000)}",
        "sentAt": datetime.now(PARIS).isoformat(timespec="seconds"),
        "from": sender,
        "to": recipients,
        "subject": subject,
        "body": body,
        "mode": delivery_mode,
        "alertCount": len(alerts),
    }
    _record_outbox(entry)
    app_log.info("Notification e-mail enregistrée pour %s (%s)", ", ".join(recipients), delivery_mode)
    return entry
