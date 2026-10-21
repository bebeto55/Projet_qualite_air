import numpy as np
import pandas as pd
import streamlit as st
import requests
from supabase import create_client

POLLUANTS = ["european_aqi", "pm10", "pm2_5", "nitrogen_dioxide",
             "ozone", "sulphur_dioxide", "carbon_monoxide", "birch_pollen"]
METEO = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m",
         "wind_u", "wind_v", "precipitation"]


def charger_df():
    url = "https://wynjcciiprpxtkvjaurm.supabase.co"
    key = st.secrets["supabase_tok"]
    supabase = create_client(url, key)

    lignes_totales, debut, taille_page = [], 0, 1000
    while True:
        rep = (supabase.table("mesures")
               .select("*")
               .order("capteur_id").order("time")      # ordre stable pour la pagination
               .range(debut, debut + taille_page - 1)
               .execute())
        lignes = rep.data
        lignes_totales.extend(lignes)
        if len(lignes) < taille_page:
            break
        debut += taille_page

    df = pd.DataFrame(lignes_totales)
    print("Nombre total de lignes :", len(df))
    return df


def preparer_df(df):
    """Conversion du temps, grille horaire par capteur, vent en composantes.
    À appeler UNE SEULE fois sur le df brut."""
    df = df.copy()
    df["time"] = (pd.to_datetime(df["time"])
                  .dt.tz_localize("Europe/Paris", ambiguous="NaT", nonexistent="shift_forward")
                  .dt.tz_convert("UTC"))
    df = df.dropna(subset=["time"])
    df = df.drop_duplicates(["capteur_id", "time"])

    df = (df.set_index("time")
            .groupby("capteur_id", observed=True)
            .resample("1h").asfreq()
            .drop(columns="capteur_id", errors="ignore")
            .reset_index())
    df = df.sort_values(["capteur_id", "time"]).reset_index(drop=True)

    rad = np.deg2rad(df["wind_direction_10m"])
    df["wind_u"] = -df["wind_speed_10m"] * np.sin(rad)
    df["wind_v"] = -df["wind_speed_10m"] * np.cos(rad)
    return df


def features_passe(df):
    """historique + past_meteo : indépendants de h, à calculer une seule fois."""
    g = df.groupby("capteur_id", observed=True)
    temps_pass = [1, 2, 3, 6, 12, 24, 48, 72, 168]
    intervalle = [6, 24, 72]

    f = {}
    for pol in POLLUANTS:
        f[f"{pol}_pass0"] = df[pol]
        for t in temps_pass:
            f[f"{pol}_pass{t}"] = g[pol].shift(t)
        for i in intervalle:
            roll = g[pol].rolling(i, min_periods=i // 2)
            f[f"{pol}_mean{i}"] = roll.mean().reset_index(level=0, drop=True)
            f[f"{pol}_std{i}"]  = roll.std().reset_index(level=0, drop=True)
            f[f"{pol}_max{i}"]  = roll.max().reset_index(level=0, drop=True)
        f[f"{pol}_dif6"]  = df[pol] - g[pol].shift(6)
        f[f"{pol}_dif24"] = df[pol] - g[pol].shift(24)
    historique = pd.DataFrame(f).astype("float32")

    met = {}
    for m in METEO:
        met[f"{m}_pass0"] = df[m]
        for t in [3, 6, 12, 24]:
            met[f"{m}_pass{t}"] = g[m].shift(t)
    past_meteo = pd.DataFrame(met).astype("float32")
    return historique, past_meteo


def features_futur(df, h):
    g = df.groupby("capteur_id", observed=True)
    out = {}
    for v in METEO:
        fen = pd.concat([g[v].shift(-k) for k in range(1, h + 1)], axis=1)
        out[f"{v}_fut_h"]    = g[v].shift(-h)
        out[f"{v}_fut_mean"] = fen.mean(axis=1)
        out[f"{v}_fut_min"]  = fen.min(axis=1)
        out[f"{v}_fut_max"]  = fen.max(axis=1)
        out[f"{v}_delta"]    = out[f"{v}_fut_h"] - df[v]
    pr = pd.concat([g["precipitation"].shift(-k) for k in range(1, h + 1)], axis=1)
    out["precip_cumul"] = pr.sum(axis=1, min_count=h)
    d = (df["time"] + pd.Timedelta(hours=h)).dt.tz_convert("Europe/Paris")
    out["hour_sin"] = np.sin(2 * np.pi * d.dt.hour / 24)
    out["hour_cos"] = np.cos(2 * np.pi * d.dt.hour / 24)
    out["dow"], out["month"] = d.dt.dayofweek, d.dt.month
    return pd.DataFrame(out).astype("float32")


########################## récupérer la prévision météo ####################################
VARS_API = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m",
            "wind_direction_10m", "precipitation"]
def prevision_meteo(lat, lon):
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon, "hourly": ",".join(VARS_API),
        "timezone": "UTC", "past_days": 1, "forecast_days": 3}, timeout=30) #past days va récupérer le nombre de jours  dans le passé
    if not r.ok:
        raise RuntimeError(r.text) #affiche le pb avec l'api                                    #forecast_days vas récupérer le nombre de jour dans le futur, on est sur d'avoir nos 24h dedans

    f = pd.DataFrame(r.json()["hourly"]) #converti en dataFrame après avoir converti en dico et sélectionne la clé "hourly qui contient les données horaires"
    f["time"] = (pd.to_datetime(f["time"])
               .dt.tz_localize("Europe/Paris", ambiguous="NaT", nonexistent="shift_forward")# convertit en heure française
               .dt.tz_convert("UTC"))
    f = f.dropna(subset=["time"])
    return f

############################################"ajout de l'historique du temps futur à l'historique météo actuel################################################"


def ajouter_previsions(df, capteurs):
    morceaux = []
    for c in capteurs:
        sub = df[df["capteur_id"].astype(str) == str(c["id"])] # sub est un dataframe qui regroupe plusieurs occurences id d'un capteur c
        if sub.empty:
            continue
        f = prevision_meteo(c["lat"], c["lon"]) 
        f = f[f["time"] > sub["time"].max()].copy()     # la météo future prenant certaine valeur du passé on l'élimine seulement après la dernière ligne connue
        f["capteur_id"] = sub["capteur_id"].iloc[0]     # on ajoute à f la cononne des id de capteurs
        morceaux.append(f)

    df = pd.concat([df] + morceaux, ignore_index=True).sort_values(["capteur_id", "time"]) # on ajoute les météo futurs et on réorganise par capteur et par time
    df = (df.set_index("time")
            .groupby("capteur_id", observed=True)
            .resample("1h").asfreq()
            .drop(columns="capteur_id", errors="ignore")# suppression de la colonne capteur id en trop
            .reset_index()) #capteur_id et time redevienne des colonnes

    rad = np.deg2rad(df["wind_direction_10m"])          # recalcul du vent pour les lignes futures
    df["wind_u"] = -df["wind_speed_10m"] * np.sin(rad)
    df["wind_v"] = -df["wind_speed_10m"] * np.cos(rad)
    return df.sort_values(["capteur_id", "time"]).reset_index(drop=True)