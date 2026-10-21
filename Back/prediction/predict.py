from datetime import timedelta
import joblib
import pandas as pd
from dico import capteurs
import gspread #pour google sheet
from importer_df import charger_df, preparer_df, features_passe, features_futur,prevision_meteo,ajouter_previsions
#pip install gspread

               # True : on se place 24 h avant la fin et on compare au réel
SIMULATION = False
df = ajouter_previsions(preparer_df(charger_df()), capteurs)
historique, past_meteo = features_passe(df)
positions = {}
noms = {str(c["id"]): c["nom"] for c in capteurs} 
for c in capteurs:
    cap = str(c["id"])
    sub = df[df["capteur_id"].astype(str) == cap]
    if SIMULATION:
        if len(sub) >= 25:
            positions[cap] = sub.index[-25]
    else:
        i = sub["european_aqi"].last_valid_index()   # dernière mesure réelle du capteur
        if i is not None:
            positions[cap] = i


bundle = joblib.load("modele_aqi/bundle_aqi.joblib")
models, columns = bundle["models"], bundle["columns"]

# 1. Données : grille préparée une seule fois, puis features passées une seule fois


# 2. Ligne t0 de chaque capteur (index de la grille, donc cohérent avec les features)


ids, pos = list(positions), list(positions.values())

# 3. Un predict par horizon pour tous les capteurs
lignes = []
for h in range(1, 25):
    X = pd.concat([historique, past_meteo, features_futur(df, h)], axis=1)[columns[h]]
    preds = models[h].predict(X.loc[pos])
    for cap, i, p in zip(ids, pos, preds):
        t0 = pd.Timestamp(df.loc[i, "time"]).tz_convert("Europe/Paris")
        lignes.append({"capteur_id": cap,
                       "heure_locale": t0 + timedelta(hours=h),
                       "aqi_predit": float(p)})

previs_df = (pd.DataFrame(lignes)
             .assign(capteur_nom=lambda d: d["capteur_id"].map(noms))
             .sort_values(["capteur_id", "heure_locale"])
             .reset_index(drop=True))

# 4. Comparaison au réel (simulation)
if SIMULATION:
    reel = (df.assign(heure_locale=df["time"].dt.tz_convert("Europe/Paris"))
              .assign(capteur_id=lambda d: d["capteur_id"].astype(str))
              .set_index(["capteur_id", "heure_locale"])["european_aqi"])
    previs_df["aqi_reel"] = [reel.get((c, t)) for c, t in
                             zip(previs_df["capteur_id"], previs_df["heure_locale"])]
    previs_df["erreur_abs"] = (previs_df["aqi_predit"] - previs_df["aqi_reel"]).abs()
    print(previs_df.groupby("capteur_id")["erreur_abs"].mean().round(2))

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)
print(previs_df.pivot(index="heure_locale", columns="capteur_id", values="aqi_predit"))







#ajout dans un google sheet
# avant ça créer une clé api pour google sheet dans le google workspace
#après connecter un google sheet spécial pour cette clée à travers l'email correspondant dans le workspace

gc = gspread.service_account(filename="credentials.json")
ws = gc.open("AQI_futures").sheet1

out = previs_df.copy()
out["heure_locale"] = out["heure_locale"].dt.strftime("%Y-%m-%d %H:%M:%S")
out = out.fillna("")

ws.clear()
ws.update([out.columns.tolist()] + out.values.tolist())