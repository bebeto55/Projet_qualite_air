"""Accès aux mesures stockées dans Supabase (table `mesures`).

Utilise directement l'API REST PostgREST de Supabase (lecture seule) et met
les résultats en cache pour garantir un dashboard < 3 s (critère MVP).
"""
from __future__ import annotations

import sys
import threading
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests
import urllib3

from logs_service import app_log
from settings import (BACK_DIR, CACHE_TTL_MEASURES, SSL_VERIFY, SUPABASE_TABLE,
                      SUPABASE_TOKEN, SUPABASE_URL)

if not SSL_VERIFY:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, str(BACK_DIR / "Projet_qualite_air"))
from dico import capteurs as CAPTEURS  # noqa: E402  (référentiel des 34 stations)

PARIS = ZoneInfo("Europe/Paris")
PAGE_SIZE = 1000

# Colonnes Supabase -> clés attendues par le frontend
FIELD_MAP = {
    "european_aqi": "aqi",
    "pm2_5": "pm25",
    "pm10": "pm10",
    "nitrogen_dioxide": "no2",
    "ozone": "o3",
    "sulphur_dioxide": "so2",
    "carbon_monoxide": "co",
    "birch_pollen": "pollen",
    "temperature_2m": "temp",
    "relative_humidity_2m": "humidity",
    "wind_speed_10m": "wind",
    "wind_direction_10m": "windDir",
    "precipitation": "precipitation",
}
NUMERIC = list(FIELD_MAP)


class SupabaseError(RuntimeError):
    pass


class _Cache:
    def __init__(self):
        self._data: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()

    def get(self, key: str, ttl: int):
        with self._lock:
            hit = self._data.get(key)
            if hit and time.time() - hit[0] < ttl:
                return hit[1]
        return None

    def set(self, key: str, value) -> None:
        with self._lock:
            self._data[key] = (time.time(), value)

    def age(self, key: str) -> float | None:
        hit = self._data.get(key)
        return time.time() - hit[0] if hit else None


cache = _Cache()
_fetch_lock = threading.Lock()


def _headers() -> dict:
    if not SUPABASE_TOKEN:
        raise SupabaseError("SUPABASE_TOKEN manquant (voir Back/api/.env.example)")
    return {"apikey": SUPABASE_TOKEN, "Authorization": f"Bearer {SUPABASE_TOKEN}"}


def fetch_measures(hours: int) -> pd.DataFrame:
    """Toutes les mesures des `hours` dernières heures (heure locale Paris)."""
    since = (datetime.now(PARIS) - timedelta(hours=hours)).replace(tzinfo=None)
    rows: list[dict] = []
    offset = 0
    session = requests.Session()
    session.verify = SSL_VERIFY
    while True:
        params = {
            "select": "*",
            "time": f"gte.{since.isoformat(timespec='seconds')}",
            "order": "capteur_id.asc,time.asc",
            "limit": PAGE_SIZE,
            "offset": offset,
        }
        try:
            r = session.get(f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}", params=params,
                            headers=_headers(), timeout=20)
        except requests.RequestException as exc:
            raise SupabaseError(f"Supabase injoignable : {exc}") from exc
        if not r.ok:
            raise SupabaseError(f"Supabase {r.status_code} : {r.text[:200]}")
        page = r.json()
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"]).dt.tz_localize(None)
    df["capteur_id"] = df["capteur_id"].astype(str)
    for col in NUMERIC:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_measures(hours: int = 192) -> pd.DataFrame:
    """Mesures en cache (8 jours par défaut, suffisant pour toutes les pages)."""
    key = f"measures:{hours}"
    df = cache.get(key, CACHE_TTL_MEASURES)
    if df is not None:
        return df
    with _fetch_lock:  # évite N requêtes simultanées vers Supabase
        df = cache.get(key, CACHE_TTL_MEASURES)
        if df is None:
            t0 = time.time()
            df = fetch_measures(hours)
            app_log.info("Supabase : %d lignes chargées en %.2fs", len(df), time.time() - t0)
            cache.set(key, df)
    return df


# ── Helpers de mise en forme ────────────────────────────────────────────────
def _num(v, digits: int = 1):
    if v is None or (isinstance(v, float) and np.isnan(v)) or pd.isna(v):
        return None
    return round(float(v), digits)


def _row_to_values(row) -> dict:
    return {FIELD_MAP[c]: _num(row.get(c), 0 if c == "european_aqi" else 1) for c in NUMERIC}


def _iso(ts: pd.Timestamp) -> str:
    return ts.tz_localize(PARIS, ambiguous="NaT", nonexistent="shift_forward").isoformat() \
        if ts.tzinfo is None else ts.isoformat()


def latest_per_sensor(df: pd.DataFrame) -> pd.DataFrame:
    valid = df.dropna(subset=["european_aqi"])
    return valid.sort_values("time").groupby("capteur_id", as_index=False).tail(1)


def build_sensors(df: pd.DataFrame) -> list[dict]:
    latest = {r["capteur_id"]: r for r in latest_per_sensor(df).to_dict("records")} if not df.empty else {}
    now = datetime.now(PARIS).replace(tzinfo=None)
    out = []
    for c in CAPTEURS:
        row = latest.get(str(c["id"]))
        base = {"id": str(c["id"]), "name": c["nom"], "lat": c["lat"], "lng": c["lon"]}
        if row is None:
            out.append({**base, "status": "offline", "lastUpdate": None})
            continue
        age_h = (now - row["time"].to_pydatetime()).total_seconds() / 3600
        out.append({
            **base,
            **_row_to_values(row),
            "lastUpdate": _iso(row["time"]),
            "status": "online" if age_h <= 3 else "offline",
        })
    return out


def build_current(df: pd.DataFrame, sensor_id: str | None = None) -> dict:
    latest = latest_per_sensor(df)
    if sensor_id:
        latest = latest[latest["capteur_id"] == str(sensor_id)]
    if latest.empty:
        raise SupabaseError("Aucune mesure récente disponible")
    means = latest[NUMERIC].mean(numeric_only=True)
    values = {FIELD_MAP[c]: _num(means[c], 0 if c == "european_aqi" else 1) for c in NUMERIC}
    worst = latest.loc[latest["european_aqi"].idxmax()]
    return {
        **values,
        "pressure": None,  # non collectée par le pipeline actuel
        "station": worst["capteur_nom"] if sensor_id else f"Moyenne Île-de-France ({len(latest)} stations)",
        "worstStation": {"id": worst["capteur_id"], "name": worst["capteur_nom"], "aqi": _num(worst["european_aqi"], 0)},
        "sensorCount": int(len(latest)),
        "updatedAt": _iso(latest["time"].max()),
    }


def build_history(df: pd.DataFrame, hours: int = 24, sensor_id: str | None = None) -> list[dict]:
    if df.empty:
        return []
    sub = df[df["capteur_id"] == str(sensor_id)] if sensor_id else df
    cutoff = sub["time"].max() - pd.Timedelta(hours=hours)
    sub = sub[sub["time"] > cutoff]
    hourly = sub.groupby(sub["time"].dt.floor("h"))[NUMERIC].mean(numeric_only=True).sort_index()
    out = []
    for ts, row in hourly.iterrows():
        values = {FIELD_MAP[c]: _num(row[c], 0 if c == "european_aqi" else 1) for c in NUMERIC}
        out.append({"time": _iso(ts), "timeLabel": ts.strftime("%d/%m %Hh") if hours > 24 else ts.strftime("%H:%M"), **values})
    return out


def build_weather(df: pd.DataFrame) -> dict:
    cur = build_current(df)
    deg = cur.get("windDir")
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
    return {
        "temp": cur["temp"],
        "feelsLike": cur["temp"],
        "humidity": cur["humidity"],
        "wind": cur["wind"],
        "windDir": dirs[int((deg % 360) / 22.5 + 0.5) % 16] if deg is not None else "—",
        "precipitation": cur["precipitation"],
        "pressure": None,
        "description": "Pluie" if (cur["precipitation"] or 0) > 0.1 else "Sec",
        "city": "Île-de-France",
        "updatedAt": cur["updatedAt"],
    }


def detect_anomalies(df: pd.DataFrame, z_threshold: float = 3.0) -> list[dict]:
    """US-010 : Z-score de la dernière mesure vs l'historique 7 j de chaque capteur."""
    out = []
    if df.empty:
        return out
    cols = {"pm2_5": "PM2.5", "pm10": "PM10", "nitrogen_dioxide": "NO2", "ozone": "O3"}
    for cid, sub in df.sort_values("time").groupby("capteur_id"):
        if len(sub) < 48:
            continue
        last = sub.iloc[-1]
        hist = sub.iloc[:-1]
        for col, label in cols.items():
            mu, sigma = hist[col].mean(), hist[col].std()
            val = last[col]
            if pd.isna(val) or not sigma or pd.isna(sigma):
                continue
            z = (val - mu) / sigma
            if abs(z) >= z_threshold:
                out.append({
                    "id": f"anomaly-{cid}-{col}",
                    "type": "anomaly",
                    "sensorId": cid,
                    "sensor": last["capteur_nom"],
                    "pollutant": label,
                    "value": _num(val),
                    "mean": _num(mu),
                    "zScore": _num(z, 2),
                    "level": "warning",
                    "ts": _iso(last["time"]),
                    "message": f"Mesure atypique {label} ({_num(val)} µg/m³, z={_num(z, 1)})",
                })
    return out


def build_bi_analytics(df: pd.DataFrame) -> dict:
    """Agrégations analytiques complètes (style Power BI) sur l'historique Supabase."""
    if df.empty:
        return {"totalRows": 0, "stationStats": [], "hourlyProfile": [], "aqiDistribution": [], "correlations": []}

    station_stats = []
    for cid, g in df.sort_values("time").groupby("capteur_id"):
        nom = g["capteur_nom"].dropna().iloc[-1] if not g["capteur_nom"].dropna().empty else cid
        last_row = g.iloc[-1]
        last_ts = last_row["time"]
        station_stats.append({
            "id": str(cid),
            "name": nom,
            "count": int(len(g)),
            "lat": _num(last_row.get("latitude"), 4),
            "lng": _num(last_row.get("longitude"), 4),
            "aqiMin": _num(g["european_aqi"].min(), 0),
            "aqiMean": _num(g["european_aqi"].mean(), 1),
            "aqiMax": _num(g["european_aqi"].max(), 0),
            "aqiLast": _num(last_row.get("european_aqi"), 0),
            "lastTime": _iso(last_ts),
            "lastDay": last_ts.strftime("%d/%m/%Y") if pd.notna(last_ts) else "—",
            "lastHour": last_ts.strftime("%H:%M:%S") if pd.notna(last_ts) else "—",
            "pm25Mean": _num(g["pm2_5"].mean(), 1),
            "pm25Max": _num(g["pm2_5"].max(), 1),
            "pm10Mean": _num(g["pm10"].mean(), 1),
            "no2Mean": _num(g["nitrogen_dioxide"].mean(), 1),
            "o3Mean": _num(g["ozone"].mean(), 1),
            "so2Mean": _num(g["sulphur_dioxide"].mean(), 1),
            "tempMean": _num(g["temperature_2m"].mean(), 1),
            "humidityMean": _num(g["relative_humidity_2m"].mean(), 1),
            "precipMean": _num(g["precipitation"].mean(), 2),
            "windMean": _num(g["wind_speed_10m"].mean(), 1),
            "windDirMean": _num(g["wind_direction_10m"].mean(), 0),
        })
    station_stats.sort(key=lambda s: s["aqiMean"] or 0, reverse=True)

    df_time = df.assign(
        hour=df["time"].dt.hour,
        day=df["time"].dt.day,
        date_str=df["time"].dt.strftime("%d/%m"),
        month_num=df["time"].dt.month,
    )
    MONTH_FR = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
    }
    hourly_profile = []
    for h, g in df_time.groupby("hour"):
        hourly_profile.append({
            "hourNum": int(h),
            "hour": f"{int(h):02d}h",
            "aqi": _num(g["european_aqi"].mean(), 1),
            "no2": _num(g["nitrogen_dioxide"].mean(), 1),
            "pm25": _num(g["pm2_5"].mean(), 1),
            "pm10": _num(g["pm10"].mean(), 1),
            "o3": _num(g["ozone"].mean(), 1),
            "temp": _num(g["temperature_2m"].mean(), 1),
            "wind": _num(g["wind_speed_10m"].mean(), 1),
        })

    daily_series = []
    for (d_str, d_num, m_num), g in df_time.sort_values("time").groupby(["date_str", "day", "month_num"], sort=False):
        daily_series.append({
            "date": d_str,
            "day": int(d_num),
            "month": MONTH_FR.get(int(m_num), str(m_num)),
            "aqiMean": _num(g["european_aqi"].mean(), 1),
            "aqiMin": _num(g["european_aqi"].min(), 0),
            "aqiMax": _num(g["european_aqi"].max(), 0),
        })

    monthly_series = []
    for m_num, g in df_time.groupby("month_num"):
        monthly_series.append({
            "month": MONTH_FR.get(int(m_num), str(m_num)),
            "aqiMean": _num(g["european_aqi"].mean(), 1),
            "aqiMin": _num(g["european_aqi"].min(), 0),
            "aqiMax": _num(g["european_aqi"].max(), 0),
        })

    raw_rows = []
    for _, r in df.sort_values("time", ascending=False).head(250).iterrows():
        ts = r["time"]
        raw_rows.append({
            "capteur_id": str(r.get("capteur_id", "")),
            "capteur_nom": str(r.get("capteur_nom", "")),
            "time": _iso(ts),
            "timeFormatted": ts.strftime("%d/%m/%Y %H:%M") if pd.notna(ts) else "—",
            "latitude": _num(r.get("latitude"), 4),
            "longitude": _num(r.get("longitude"), 4),
            "european_aqi": _num(r.get("european_aqi"), 0),
            "nitrogen_dioxide": _num(r.get("nitrogen_dioxide"), 2),
            "ozone": _num(r.get("ozone"), 2),
            "pm10": _num(r.get("pm10"), 2),
            "pm2_5": _num(r.get("pm2_5"), 2),
            "precipitation": _num(r.get("precipitation"), 2),
            "relative_humidity_2m": _num(r.get("relative_humidity_2m"), 1),
            "sulphur_dioxide": _num(r.get("sulphur_dioxide"), 2),
            "temperature_2m": _num(r.get("temperature_2m"), 1),
            "wind_direction_10m": _num(r.get("wind_direction_10m"), 0),
            "wind_speed_10m": _num(r.get("wind_speed_10m"), 1),
        })

    aqi_series = df["european_aqi"].dropna()
    total_aqi = max(len(aqi_series), 1)
    bins = [
        ("Bon (0-20)", (aqi_series <= 20).sum(), "#22c55e"),
        ("Correct (20-40)", ((aqi_series > 20) & (aqi_series <= 40)).sum(), "#84cc16"),
        ("Moyen (40-60)", ((aqi_series > 40) & (aqi_series <= 60)).sum(), "#f59e0b"),
        ("Médiocre (60-80)", ((aqi_series > 60) & (aqi_series <= 80)).sum(), "#f97316"),
        ("Très médiocre (>80)", (aqi_series > 80).sum(), "#ef4444"),
    ]
    aqi_distribution = [
        {"label": label, "count": int(cnt), "pct": round(float(cnt) * 100 / total_aqi, 1), "color": col}
        for label, cnt, col in bins
    ]

    corr_cols = ["european_aqi", "pm2_5", "pm10", "nitrogen_dioxide", "ozone",
                 "temperature_2m", "relative_humidity_2m", "wind_speed_10m"]
    corr_df = df[corr_cols].corr()
    pairs = [
        ("Vent vs PM2.5", "wind_speed_10m", "pm2_5"),
        ("Vent vs NO₂", "wind_speed_10m", "nitrogen_dioxide"),
        ("Température vs O₃", "temperature_2m", "ozone"),
        ("Humidité vs PM10", "relative_humidity_2m", "pm10"),
        ("NO₂ vs EAQI", "nitrogen_dioxide", "european_aqi"),
        ("PM2.5 vs PM10", "pm2_5", "pm10"),
    ]
    correlations = [
        {"pair": label, "r": _num(corr_df.loc[a, b], 2)}
        for label, a, b in pairs if a in corr_df and b in corr_df
    ]

    return {
        "totalRows": int(len(df)),
        "fromDate": _iso(df["time"].min()),
        "toDate": _iso(df["time"].max()),
        "aqiMin": _num(aqi_series.min(), 0) if not aqi_series.empty else 0,
        "aqiMean": _num(aqi_series.mean(), 1) if not aqi_series.empty else 0,
        "aqiMax": _num(aqi_series.max(), 0) if not aqi_series.empty else 0,
        "stationStats": station_stats,
        "hourlyProfile": hourly_profile,
        "dailySeries": daily_series,
        "monthlySeries": monthly_series,
        "rawTable": raw_rows,
        "aqiDistribution": aqi_distribution,
        "correlations": correlations,
    }
