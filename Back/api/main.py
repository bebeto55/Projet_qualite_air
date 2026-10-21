"""API REST Smart City — pont entre Supabase / modèle IA et le frontend React.

Lancement :  uvicorn main:app --reload --port 8080   (depuis Back/api)
Documentation interactive : http://localhost:8080/docs
"""
from __future__ import annotations

import threading
import time

import requests
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, EmailStr, Field

import alerts_service
import data_service as ds
from auth import admin_user, authenticate, current_user
from logs_service import app_log, memory_handler, metrics, security_log, setup_logging
from settings import (CORS_ORIGINS, POWERBI_CLIENT_ID, POWERBI_CLIENT_SECRET,
                      POWERBI_PASSWORD, POWERBI_REPORT_ID, POWERBI_TENANT_ID,
                      POWERBI_USERNAME, POWERBI_WORKSPACE_ID, SSL_VERIFY,
                      SUPABASE_TOKEN)

setup_logging()

app = FastAPI(title="Smart City — Qualité de l'air", version="1.0.0",
              description="API de la plateforme de suivi de la qualité de l'air (Île-de-France).")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


# ── Middleware : temps de réponse + logs détaillés (US-017/018) ─────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        app_log.exception("Erreur non gérée sur %s %s", request.method, request.url.path)
        response = JSONResponse({"message": "Erreur interne du serveur"}, status_code=500)
    ms = (time.perf_counter() - t0) * 1000
    route = request.scope.get("route")
    metrics.record(getattr(route, "path", request.url.path), response.status_code, ms)
    if request.url.path.startswith("/api"):
        app_log.info("%s %s -> %d (%.0f ms)", request.method, request.url.path, response.status_code, ms)
    response.headers["X-Response-Time-ms"] = f"{ms:.0f}"
    return response


@app.exception_handler(ds.SupabaseError)
async def supabase_error(_: Request, exc: ds.SupabaseError):
    app_log.error("Supabase : %s", exc)
    return JSONResponse({"message": str(exc)}, status_code=503)


@app.exception_handler(HTTPException)
async def http_error(_: Request, exc: HTTPException):
    return JSONResponse({"message": exc.detail}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def generic_error(_: Request, exc: Exception):
    app_log.error("Erreur serveur non gérée : %s", exc)
    return JSONResponse({"message": f"Erreur serveur : {exc}"}, status_code=500)


@app.on_event("startup")
def warmup():
    """Pré-charge les mesures et les prévisions pour un premier affichage rapide."""
    def _run():
        try:
            ds.get_measures()
            from ml_service import get_predictions
            get_predictions()
        except Exception as exc:  # noqa: BLE001 — on ne bloque pas le démarrage
            app_log.warning("Préchargement incomplet : %s", exc)
    threading.Thread(target=_run, daemon=True).start()


# ── Schémas ─────────────────────────────────────────────────────────────────
class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=1, max_length=128)


class Thresholds(BaseModel):
    pm25: float = Field(ge=1, le=500)
    pm10: float = Field(ge=1, le=600)
    no2: float = Field(ge=1, le=1000)
    o3: float = Field(ge=1, le=1000)


class AlertConfigIn(BaseModel):
    thresholds: Thresholds
    notifications: dict[str, bool] = {"email": True, "sms": False}
    recipients: list[EmailStr] = []


# ── Santé / monitoring ──────────────────────────────────────────────────────
@app.get("/api/health", tags=["monitoring"])
def health():
    age = ds.cache.age("measures:192")
    return {"status": "ok", "supabaseConfigured": bool(SUPABASE_TOKEN),
            "measuresCacheAgeSeconds": round(age) if age is not None else None}


@app.get("/api/metrics", tags=["monitoring"])
def get_metrics(_: dict = Depends(admin_user)):
    return metrics.snapshot()


@app.get("/api/logs", tags=["monitoring"])
def get_logs(limit: int = Query(200, ge=1, le=500), level: str | None = None,
             _: dict = Depends(admin_user)):
    records = list(memory_handler.records)
    if level:
        records = [r for r in records if r["level"] == level.upper()]
    return list(reversed(records[-limit:]))


# ── Authentification ────────────────────────────────────────────────────────
@app.post("/api/auth/login", tags=["auth"])
def login(body: LoginIn, request: Request):
    return authenticate(body.username, body.password, request.client.host if request.client else "?")


@app.get("/api/auth/me", tags=["auth"])
def me(user: dict = Depends(current_user)):
    return user


# ── Qualité de l'air ────────────────────────────────────────────────────────
@app.get("/api/sensors", tags=["air"])
def sensors():
    return ds.build_sensors(ds.get_measures())


@app.get("/api/air-quality/current", tags=["air"])
def current(sensor_id: str | None = Query(None, max_length=20)):
    return ds.build_current(ds.get_measures(), sensor_id)


@app.get("/api/air-quality/history", tags=["air"])
def history(hours: int = Query(24, ge=1, le=192), sensor_id: str | None = Query(None, max_length=20)):
    return ds.build_history(ds.get_measures(), hours, sensor_id)


@app.get("/api/weather/current", tags=["air"])
def weather():
    return ds.build_weather(ds.get_measures())


@app.get("/api/anomalies", tags=["air"])
def anomalies():
    return ds.detect_anomalies(ds.get_measures())


# ── Prévisions IA ───────────────────────────────────────────────────────────
@app.get("/api/predictions", tags=["ia"])
def predictions():
    from ml_service import get_predictions
    try:
        return get_predictions()
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc))
    except Exception as exc:  # noqa: BLE001
        app_log.exception("Échec du calcul des prévisions")
        raise HTTPException(503, f"Prévisions indisponibles : {exc}")


@app.post("/api/predictions/refresh", tags=["ia"])
def refresh_predictions(user: dict = Depends(admin_user)):
    from ml_service import get_predictions
    security_log.info("Recalcul des prévisions demandé par %s", user["username"])
    return get_predictions(force=True)


# ── Alertes ─────────────────────────────────────────────────────────────────
@app.get("/api/alerts", tags=["alertes"])
def alerts():
    df = ds.get_measures()
    return alerts_service.build_alerts(df) + ds.detect_anomalies(df)


@app.post("/api/alerts/{alert_id}/acknowledge", tags=["alertes"])
def acknowledge(alert_id: str, user: dict = Depends(current_user)):
    alerts_service.acknowledge(alert_id[:100])
    security_log.info("Alerte %s acquittée par %s", alert_id[:100], user["username"])
    return {"ok": True}


@app.get("/api/alerts/config", tags=["alertes"])
def alert_config(_: dict = Depends(current_user)):
    return alerts_service.load_config()


@app.put("/api/alerts/config", tags=["alertes"])
def update_alert_config(body: AlertConfigIn, user: dict = Depends(admin_user)):
    security_log.info("Seuils d'alerte modifiés par %s : %s", user["username"], body.thresholds.model_dump())
    return alerts_service.save_config(body.model_dump())


@app.post("/api/alerts/test-email", tags=["alertes"])
def test_email(user: dict = Depends(admin_user)):
    cfg = alerts_service.load_config()
    recipients = cfg.get("recipients") or ["marie.dubois@metropole.fr"]
    df = ds.get_measures()
    active = alerts_service.build_alerts(df)
    sample = active[:3] if active else [{
        "sensor": "Nogent-sur-Marne (Test)",
        "pollutant": "PM2.5",
        "value": 54.2,
        "threshold": cfg["thresholds"]["pm25"],
    }]
    mail = alerts_service.send_email(sample, recipients)
    return {"ok": True, "email": mail}


@app.get("/api/alerts/emails", tags=["alertes"])
def list_alert_emails(_: dict = Depends(current_user)):
    return alerts_service.get_sent_emails(20)


@app.post("/api/powerbi/connect-datasource", tags=["powerbi"])
def connect_pbi_datasource():
    """Injecte automatiquement les identifiants PostgreSQL Supabase dans Power BI Service et rafraîchit le modèle."""
    import json as _json
    tok = requests.post(
        f"https://login.microsoftonline.com/{POWERBI_TENANT_ID}/oauth2/v2.0/token",
        data={
            "grant_type": "password",
            "client_id": POWERBI_CLIENT_ID,
            "username": POWERBI_USERNAME,
            "password": POWERBI_PASSWORD,
            "scope": "https://analysis.windows.net/powerbi/api/.default openid profile offline_access",
        },
        verify=SSL_VERIFY,
        timeout=20,
    )
    if not tok.ok or "access_token" not in tok.json():
        raise HTTPException(502, "Authentification Power BI Service échouée")
    H = {"Authorization": f"Bearer {tok.json()['access_token']}", "Content-Type": "application/json"}
    rep = requests.get(f"https://api.powerbi.com/v1.0/myorg/reports/{POWERBI_REPORT_ID}", headers=H, verify=SSL_VERIFY, timeout=20).json()
    dataset_id = rep["datasetId"]
    datasources = requests.get(f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/datasources", headers=H, verify=SSL_VERIFY, timeout=20).json().get("value", [])
    pg_ds = next((d for d in datasources if d.get("datasourceType") == "PostgreSql"), None)
    if not pg_ds:
        raise HTTPException(404, "Aucune source PostgreSQL trouvée sur le dataset")
    gw_id, ds_id = pg_ds["gatewayId"], pg_ds["datasourceId"]
    creds = _json.dumps({
        "credentialData": [
            {"name": "username", "value": "postgres.wynjcciiprpxtkvjaurm"},
            {"name": "password", "value": "Esic35!!!poli"},
        ]
    })
    last_err = ""
    for enc in ("NotEncrypted", "Encrypted"):
        r = requests.patch(
            f"https://api.powerbi.com/v1.0/myorg/gateways/{gw_id}/datasources/{ds_id}",
            headers=H,
            json={"credentialDetails": {
                "credentialType": "Basic",
                "credentials": creds,
                "encryptedConnection": enc,
                "encryptionAlgorithm": "None",
                "privacyLevel": "Organizational",
            }},
            verify=SSL_VERIFY,
            timeout=20,
        )
        if r.ok:
            requests.post(f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes", headers=H, json={"notifyOption": "NoNotification"}, verify=SSL_VERIFY, timeout=20)
            ds.cache.set("pbi_embed", None)
            return {"ok": True, "mode": enc, "message": "Source PostgreSQL connectée et rafraîchissement lancé !"}
        last_err = r.text[:300]
    raise HTTPException(400, f"Supabase bloque encore la connexion non-SSL : décochez 'Enforce SSL on incoming connections' dans Supabase Database Settings ({last_err})")


# ── Power BI Embedded & Analytics ───────────────────────────────────────────
@app.get("/api/powerbi/analytics", tags=["powerbi"])
def powerbi_analytics(hours: int = Query(192, ge=24, le=720)):
    """Agrégations BI temps réel sur Supabase pour le tableau de bord Power BI."""
    df = ds.get_measures(hours)
    bi = ds.build_bi_analytics(df)
    try:
        pred = ml_service.predict_station(df, None)
        bi["forecast24h"] = pred.get("forecast", [])
    except Exception:
        bi["forecast24h"] = []
    return bi


@app.get("/api/powerbi/ssl-cert", tags=["powerbi"])
def powerbi_ssl_cert():
    """Télécharge le certificat SSL racine Supabase (Back/prod-ca-2021.crt) pour Power BI Gateway / Desktop."""
    cert_path = ds.BACK_DIR / "prod-ca-2021.crt"
    if not cert_path.exists():
        raise HTTPException(404, "Certificat prod-ca-2021.crt introuvable")
    return FileResponse(cert_path, media_type="application/x-x509-ca-cert", filename="prod-ca-2021.crt")


@app.post("/api/powerbi/install-ssl-cert", tags=["powerbi"])
def install_pbi_ssl_cert():
    """Installe automatiquement Back/prod-ca-2021.crt dans le magasin Windows des Autorités de certification."""
    import subprocess
    cert_path = ds.BACK_DIR / "prod-ca-2021.crt"
    if not cert_path.exists():
        raise HTTPException(404, "Certificat prod-ca-2021.crt introuvable")
    res_ca = subprocess.run(
        ["certutil", "-user", "-addstore", "-f", "CA", str(cert_path)],
        capture_output=True,
        text=True,
        timeout=5,
    )
    subprocess.Popen(["certutil", "-user", "-addstore", "-f", "Root", str(cert_path)])
    return {
        "ok": True,
        "certPath": str(cert_path),
        "issuer": "CN=Supabase Root 2021 CA, O=Supabase Inc",
        "output": (res_ca.stdout or "Certificat enregistré. Si une fenêtre de sécurité Windows apparaît, cliquez sur « Oui ».").strip(),
    }


@app.get("/api/powerbi/dataset.csv", tags=["powerbi"], response_class=PlainTextResponse)
def powerbi_dataset_csv(hours: int = Query(192, ge=24, le=720)):
    """Flux CSV direct connectable dans Power BI Desktop via Obtenir les données -> Web."""
    df = ds.get_measures(hours)
    return df.to_csv(index=False)


@app.get("/api/powerbi/sweetviz", tags=["powerbi"])
def powerbi_sweetviz():
    """Sert le rapport d'analyse exploratoire d'origine (Back/Projet_qualite_air/rapport_qualite_air.html)."""
    report_path = ds.BACK_DIR / "Projet_qualite_air" / "rapport_qualite_air.html"
    if not report_path.exists():
        raise HTTPException(404, "rapport_qualite_air.html introuvable")
    return FileResponse(report_path, media_type="text/html")


@app.get("/api/reports/project-pdf", tags=["rapports"])
def download_project_pdf():
    """Télécharge le mémoire / dossier PDF académique et technique complet du projet."""
    root = ds.BACK_DIR.parent
    pdf_path = root / "Rapport_Academique_Smart_City.pdf"
    if not pdf_path.exists():
        pdf_path = root / "Rapport_Projet_Smart_City.pdf"
    if not pdf_path.exists():
        raise HTTPException(404, "Rapport PDF introuvable")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Rapport_Academique_Smart_City.pdf")


@app.get("/api/powerbi/embed-config", tags=["powerbi"])
def powerbi_config():
    """Récupère automatiquement le token AAD et l'embedUrl du rapport 'Smart_City' sur Power BI Service."""
    cached = ds.cache.get("pbi_embed", 1800)
    if cached is not None:
        return cached

    if POWERBI_USERNAME and POWERBI_PASSWORD and POWERBI_REPORT_ID:
        tok = requests.post(
            f"https://login.microsoftonline.com/{POWERBI_TENANT_ID}/oauth2/v2.0/token",
            data={
                "grant_type": "password",
                "client_id": POWERBI_CLIENT_ID,
                "username": POWERBI_USERNAME,
                "password": POWERBI_PASSWORD,
                "scope": "https://analysis.windows.net/powerbi/api/.default openid profile offline_access",
            },
            verify=SSL_VERIFY,
            timeout=20,
        )
        if not tok.ok or "access_token" not in tok.json():
            raise HTTPException(502, "Authentification Power BI Service échouée")
        access_token = tok.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        base = (
            f"https://api.powerbi.com/v1.0/myorg/groups/{POWERBI_WORKSPACE_ID}/reports/{POWERBI_REPORT_ID}"
            if POWERBI_WORKSPACE_ID
            else f"https://api.powerbi.com/v1.0/myorg/reports/{POWERBI_REPORT_ID}"
        )
        report = requests.get(base, headers=headers, verify=SSL_VERIFY, timeout=20)
        pages_res = requests.get(f"{base}/pages", headers=headers, verify=SSL_VERIFY, timeout=20)
        if not report.ok:
            raise HTTPException(502, "Rapport Power BI introuvable sur le workspace")
        rep_json = report.json()
        pages = pages_res.json().get("value", []) if pages_res.ok else []
        cfg = {
            "reportId": rep_json["id"],
            "reportName": rep_json.get("name", "Smart_City"),
            "embedUrl": rep_json["embedUrl"],
            "webUrl": rep_json.get("webUrl"),
            "token": access_token,
            "accessToken": access_token,
            "tokenType": "aad",
            "pages": [{"name": p["name"], "displayName": p["displayName"]} for p in pages],
        }
        ds.cache.set("pbi_embed", cfg)
        return cfg

    raise HTTPException(404, "Power BI non configuré")
