import pandas as pd
import requests
import streamlit as st
from supabase import create_client


def initialisation_tab(capteurs, mode="hourly"):

    df_air = pd.DataFrame()
    df_meteo = pd.DataFrame()

    print("Début du téléchargement...")

    for c in capteurs:

        # ============================================================
        # QUALITÉ DE L'AIR
        # ============================================================

        if mode == "hourly":

            url_air = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality?"
                f"latitude={c['lat']}&longitude={c['lon']}&"
                f"hourly=european_aqi,pm10,pm2_5,nitrogen_dioxide,"
                f"ozone,sulphur_dioxide,carbon_monoxide,birch_pollen&"
                f"forecast_hours=0&"
                f"past_hours=1000"
            )

        elif mode == "current":

            url_air = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality?"
                f"latitude={c['lat']}&longitude={c['lon']}&"
                f"current=european_aqi,pm10,pm2_5,nitrogen_dioxide,"
                f"ozone,sulphur_dioxide,carbon_monoxide,birch_pollen"
            )

        else:
            raise ValueError("mode doit être 'hourly' ou 'current'")


        # ============================================================
        # MÉTÉO
        # ============================================================

        if mode == "hourly":

            url_meteo = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={c['lat']}&longitude={c['lon']}&"
                f"hourly=temperature_2m,relative_humidity_2m,"
                f"wind_speed_10m,wind_direction_10m,precipitation&"
                f"forecast_hours=0&"
                f"past_hours=1000"
            )

        elif mode == "current":

            url_meteo = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={c['lat']}&longitude={c['lon']}&"
                f"current=temperature_2m,relative_humidity_2m,"
                f"wind_speed_10m,wind_direction_10m,precipitation"
            )


        # ============================================================
        # TÉLÉCHARGEMENT AIR
        # ============================================================

        response_air = requests.get(url_air)

        if response_air.status_code == 200:

            data_air = response_air.json()

            if mode == "hourly":
                df_temp = pd.DataFrame(data_air["hourly"])

            else:
                df_temp = pd.DataFrame([data_air["current"]])

            df_temp["capteur_id"] = c["id"]
            df_temp["capteur_nom"] = c["nom"]
            df_temp["latitude"] = c["lat"]
            df_temp["longitude"] = c["lon"]

            df_air = pd.concat(
                [df_air, df_temp],
                ignore_index=True
            )

            print(f" {c['nom']} : qualité de l'air traité")


        # ============================================================
        # TÉLÉCHARGEMENT MÉTÉO
        # ============================================================

        response_meteo = requests.get(url_meteo)

        if response_meteo.status_code == 200:

            data_meteo = response_meteo.json()

            if mode == "hourly":
                df_met = pd.DataFrame(data_meteo["hourly"])

            else:
                df_met = pd.DataFrame([data_meteo["current"]])

            df_met["capteur_id"] = c["id"]
            df_met["capteur_nom"] = c["nom"]
            df_met["latitude"] = c["lat"]
            df_met["longitude"] = c["lon"]

            df_meteo = pd.concat(
                [df_meteo, df_met],
                ignore_index=True
            )

            print(f" {c['nom']} : météo traité")


   
    # AIR + MÉTÉO
    #eviter une colonne qui se crée à cause du merg
    df_air = df_air.drop(columns=["interval"], errors="ignore")
    df_meteo = df_meteo.drop(columns=["interval"], errors="ignore")

    #arrondir le temps
    df_air["time"] = pd.to_datetime(df_air["time"], utc=True).dt.floor("h")
    df_meteo["time"] = pd.to_datetime(df_meteo["time"], utc=True).dt.floor("h")

    df_final = pd.merge(
        df_air,
        df_meteo,
        on=[
            "time",
            "capteur_id",
            "capteur_nom",
            "latitude",
            "longitude"
        ],
        how="inner"
    )

    print("✅ Fusion air + météo réussie.")

    return df_final





#connexion et création
#%pip install supabase



def envoyer_dataframe(df, table, batch_size=1000):

    df = df.copy()

    if "time" in df.columns:
        df["time"] = df["time"].astype(str)

    df = df.where(pd.notnull(df), None)

    data = df.to_dict(orient="records")

    total_envoye = 0

    for debut in range(0, len(data), batch_size):

        fin = min(debut + batch_size, len(data))
        lot = data[debut:fin]

        response = (
            supabase
            .table(table)
            .upsert(
                lot,
                on_conflict="capteur_id,time",
                ignore_duplicates=True
            )
            .execute()
        )

        nb_ajoutees = len(response.data)
        total_envoye += nb_ajoutees

        print(
            f"✅ Lot : {nb_ajoutees} nouvelles données "
            f"({fin}/{len(data)} traitées)"
        )

    print(f" Total ajouté : {total_envoye}")

    return total_envoye








