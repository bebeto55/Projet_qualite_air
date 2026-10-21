"""Prévisions IA de l'indice européen de qualité de l'air (US-009 / US-011).

Réutilise tel quel le pipeline de l'équipe data (Back/prediction/importer_df.py)
et le bundle entraîné (24 modèles, un par horizon h = 1..24 h).
La fiabilité est mesurée par un back-test : on rejoue le modèle 24 h en arrière
et on compare aux valeurs réellement observées.
"""
from __future__ import annotations

import sys
import threading
import time
import types
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import joblib
import numpy as np
import pandas as pd

from data_service import CAPTEURS, PARIS, cache, get_measures
from logs_service import app_log
from settings import CACHE_TTL_PREDICTIONS, MODEL_PATH, PREDICTION_DIR, SSL_VERIFY

# importer_df importe streamlit et supabase uniquement pour charger_df(), que l'API n'utilise pas.
for _mod_name in ("streamlit", "supabase"):
    if _mod_name not in sys.modules:
        _m = types.ModuleType(_mod_name)
        _m.create_client = lambda *a, **kw: None  # type: ignore[attr-defined]
        sys.modules[_mod_name] = _m


sys.path.insert(0, str(PREDICTION_DIR))
import importer_df  # noqa: E402
import requests as _requests  # noqa: E402

if not SSL_VERIFY:
    _orig_get = _requests.get
    _requests.get = lambda *a, **kw: _orig_get(*a, **{**kw, "verify": False})


HORIZONS = range(1, 25)
Z_80 = 1.28  # intervalle de confiance à 80 %
JOURS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

_bundle = None
_bundle_lock = threading.Lock()
_compute_lock = threading.Lock()


def load_bundle():
    global _bundle
    with _bundle_lock:
        if _bundle is None:
            if not MODEL_PATH.exists():
                raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")
            _bundle = joblib.load(MODEL_PATH)
            app_log.info("Modèle chargé : %s (%d horizons)", MODEL_PATH.name, len(_bundle["models"]))
    return _bundle


def _add_weather_forecasts(df: pd.DataFrame) -> pd.DataFrame:
    """Appelle importer_df.ajouter_previsions avec les appels Open-Meteo parallélisés."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        forecasts = dict(zip(
            [(c["lat"], c["lon"]) for c in CAPTEURS],
            pool.map(lambda c: importer_df.prevision_meteo(c["lat"], c["lon"]), CAPTEURS),
        ))
    original = importer_df.prevision_meteo
    importer_df.prevision_meteo = lambda lat, lon: forecasts[(lat, lon)].copy()
    try:
        return importer_df.ajouter_previsions(df, CAPTEURS)
    finally:
        importer_df.prevision_meteo = original


def _predict_at(models, columns, df, historique, past_meteo, positions: dict[str, int]) -> pd.DataFrame:
    ids, pos = list(positions), list(positions.values())
    lignes = []
    for h in HORIZONS:
        X = pd.concat([historique, past_meteo, importer_df.features_futur(df, h)], axis=1)[columns[h]]
        preds = models[h].predict(X.loc[pos])
        for cap, i, p in zip(ids, pos, preds):
            lignes.append({"capteur_id": cap, "h": h, "i": i, "aqi_predit": float(p)})
    return pd.DataFrame(lignes)


def compute_predictions() -> dict:
    t0 = time.time()
    bundle = load_bundle()
    models, columns = bundle["models"], bundle["columns"]

    # 10 jours d'historique : couvre le plus grand lag (168 h) + fenêtres glissantes
    raw = get_measures(240).drop(columns=["id"], errors="ignore")
    if raw.empty:
        raise RuntimeError("Pas de données en base pour lancer la prédiction")
    df = _add_weather_forecasts(importer_df.preparer_df(raw))
    df["capteur_id"] = df["capteur_id"].astype(str)
    historique, past_meteo = importer_df.features_passe(df)

    live, backtest = {}, {}
    for cap, sub in df.groupby("capteur_id"):
        i = sub["european_aqi"].last_valid_index()
        if i is None:
            continue
        live[cap] = i
        j = i - 24
        if j in sub.index:
            backtest[cap] = j

    # 1) Prévisions réelles à partir de la dernière mesure
    pred = _predict_at(models, columns, df, historique, past_meteo, live)
    pred["time"] = [pd.Timestamp(df.loc[i, "time"]).tz_convert(PARIS) + timedelta(hours=int(h))
                    for i, h in zip(pred["i"], pred["h"])]

    # 2) Back-test : fiabilité par horizon
    bt = _predict_at(models, columns, df, historique, past_meteo, backtest)
    bt["reel"] = [df.loc[i + h, "european_aqi"] for i, h in zip(bt["i"], bt["h"])]
    bt = bt.dropna(subset=["reel"])
    bt["err"] = bt["aqi_predit"] - bt["reel"]
    per_h = bt.groupby("h").apply(lambda g: pd.Series({
        "mae": g["err"].abs().mean(),
        "rmse": float(np.sqrt((g["err"] ** 2).mean())),
        "mape": (g["err"].abs() / g["reel"].clip(lower=1)).mean() * 100,
    }), include_groups=False)

    def metric(h, name, default):
        return float(per_h.loc[h, name]) if h in per_h.index else default

    noms = {str(c["id"]): c["nom"] for c in CAPTEURS}
    city = []
    for h, g in pred.groupby("h"):
        mean = float(g["aqi_predit"].mean())
        rmse = metric(h, "rmse", 5.0)
        conf = max(0.0, min(100.0, 100 - metric(h, "mape", 30.0)))
        ts = g["time"].iloc[0]
        city.append({
            "h": int(h),
            "date": ts.isoformat(),
            "dateLabel": f"{JOURS[ts.weekday()]} {ts.hour:02d}h",
            "predicted": round(mean, 1),
            "lower": round(max(0.0, mean - Z_80 * rmse), 1),
            "upper": round(mean + Z_80 * rmse, 1),
            "max": round(float(g["aqi_predit"].max()), 1),
            "aqi": round(mean),
            "confidence": round(conf),
            "mae": round(metric(h, "mae", float("nan")), 2),
        })

    sensors = {}
    for cap, g in pred.groupby("capteur_id"):
        g = g.sort_values("h")
        sensors[cap] = {
            "name": noms.get(cap, cap),
            "series": [{"h": int(h), "date": t.isoformat(), "predicted": round(p, 1)}
                       for h, t, p in zip(g["h"], g["time"], g["aqi_predit"])],
            "max24h": round(float(g["aqi_predit"].max()), 1),
        }

    overall_mae = float(bt["err"].abs().mean()) if not bt.empty else None
    overall_mape = float((bt["err"].abs() / bt["reel"].clip(lower=1)).mean() * 100) if not bt.empty else None
    worst = max(sensors.items(), key=lambda kv: kv[1]["max24h"]) if sensors else None

    result = {
        "generatedAt": pd.Timestamp.now(tz=PARIS).isoformat(),
        "computeSeconds": round(time.time() - t0, 1),
        "target": "european_aqi",
        "unit": "EAQI",
        "city": city,
        "sensors": sensors,
        "summary": {
            "next24hMean": round(float(np.mean([c["predicted"] for c in city])), 1) if city else None,
            "next24hMax": round(max(c["max"] for c in city), 1) if city else None,
            "worstSensor": {"id": worst[0], "name": worst[1]["name"], "max24h": worst[1]["max24h"]} if worst else None,
        },
        "model": {
            "name": type(next(iter(models.values())) if isinstance(models, dict) else models[1]).__name__,
            "horizons": len(HORIZONS),
            "features": len(columns[1]),
            "backtestSamples": int(len(bt)),
            "mae": round(overall_mae, 2) if overall_mae is not None else None,
            "mape": round(overall_mape, 1) if overall_mape is not None else None,
            "reliability": round(max(0.0, 100 - overall_mape), 1) if overall_mape is not None else None,
        },
    }
    app_log.info("Prévisions calculées en %.1fs (%d capteurs, MAE back-test=%s)",
                 result["computeSeconds"], len(sensors), result["model"]["mae"])
    return result


def get_predictions(force: bool = False) -> dict:
    if not force:
        hit = cache.get("predictions", CACHE_TTL_PREDICTIONS)
        if hit is not None:
            return hit
    with _compute_lock:
        hit = None if force else cache.get("predictions", CACHE_TTL_PREDICTIONS)
        if hit is None:
            hit = compute_predictions()
            cache.set("predictions", hit)
    return hit
