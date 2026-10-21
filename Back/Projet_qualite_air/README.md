# Qualité de l'air et météo en Île-de-France

Pipeline de collecte de données de **qualité de l'air** et de **météo** pour 34 points de mesure situés en Île-de-France et alentours. Les données sont récupérées via l'API [Open-Meteo](https://open-meteo.com/), fusionnées, puis stockées dans une base **Supabase** (PostgreSQL), table `mesures`.

## Fonctionnement

1. **Initialisation (historique)** : `app_historique.py` télécharge environ 1 800 heures d'historique (≈ 75 jours) pour chaque capteur, vide la table `mesures` puis y insère les données.
2. **Mise à jour (streaming)** : `app_streaming.py` récupère la mesure courante de chaque capteur (34 lignes) et l'ajoute à la base. Il est prévu pour être exécuté toutes les 30 minutes.

Pour chaque capteur, deux appels API sont effectués (air et météo), puis les résultats sont fusionnés sur `time`, `capteur_id`, `capteur_nom`, `latitude` et `longitude`. Les horodatages sont arrondis à l'heure et convertis en heure de Paris (`Europe/Paris`).

### Variables collectées

| Catégorie | Variables |
|---|---|
| Qualité de l'air | `european_aqi`, `pm10`, `pm2_5`, `nitrogen_dioxide`, `ozone`, `sulphur_dioxide`, `carbon_monoxide`, `birch_pollen` |
| Météo | `temperature_2m`, `relative_humidity_2m`, `wind_speed_10m`, `wind_direction_10m`, `precipitation` |

## Structure du projet

| Fichier | Rôle |
|---|---|
| `dico.py` | Liste des 34 capteurs (identifiant, nom, latitude, longitude) |
| `fonctions_de_chargement.py` | `initialisation_tab()` : téléchargement et fusion air + météo (modes `hourly` et `current`) ; `envoyer_dataframe()` : envoi par lots vers Supabase |
| `app_historique.py` | Chargement initial de l'historique (vide puis remplit la table) |
| `app_streaming.py` | Récupération périodique des mesures courantes, avec journalisation dans `log.txt` |
| `launcher_for_BD_1.py` | Installe les bibliothèques nécessaires à la partie base de données (`dotenv`, `supabase`, `sweetviz`, `streamlit`) |
| `launcher_for_algo.py` | Installe les bibliothèques nécessaires à la partie modélisation (`scikit-learn`, `xgboost`) |
| `requirements.txt` | Dépendances Python figées |
| `log.txt` | Journal d'exécution généré par `app_streaming.py` |

## Prérequis

- Python 3.10 ou supérieur
- Un projet [Supabase](https://supabase.com/) contenant :
  - une table `mesures` avec une contrainte d'unicité sur `(capteur_id, time)` ;
  - une fonction RPC `vider_mesures` qui vide la table.

## Installation

```bash
git clone <url-du-depot>
cd <nom-du-depot>

python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

pip install -r requirements.txt
```

Vous pouvez aussi utiliser les scripts d'installation légers : `python launcher_for_BD_1.py` et `python launcher_for_algo.py`.

## Configuration

Les clés d'accès ne doivent **jamais** être versionnées.

**Pour `app_streaming.py`**, créez un fichier `.env` à côté du script :

```env
SUPABASE_TOKEN=votre_cle_supabase
```

**Pour `app_historique.py`**, la clé est lue via les secrets Streamlit. Créez `.streamlit/secrets.toml` :

```toml
supabase_tok = "votre_cle_supabase"
```

Pensez à ajouter `.env` et `.streamlit/secrets.toml` à votre `.gitignore`.

## Utilisation

### 1. Charger l'historique

```bash
streamlit run app_historique.py
```

> ⚠️ Ce script **vide la table `mesures`** avant de la remplir. À n'utiliser que pour une initialisation ou une réinitialisation complète.

### 2. Lancer une mise à jour

```bash
python app_streaming.py
```

Le script effectue une seule récupération par exécution. La boucle `while True` avec `time.sleep(1800)` est commentée dans le code. Pour une collecte toutes les 30 minutes, planifiez l'exécution avec :

- **Linux / macOS** : `cron`, par exemple `*/30 * * * * cd /chemin/projet && python app_streaming.py`
- **Windows** : le Planificateur de tâches

Chaque exécution est tracée dans `log.txt` (nombre de lignes récupérées et message de prochaine récupération).

## Gestion des doublons

L'envoi vers Supabase utilise un `upsert` sur `(capteur_id, time)` avec `ignore_duplicates=True` : une mesure déjà présente n'est pas réinsérée. Il est donc sans risque de relancer une collecte.

## Technologies

Python, pandas, requests, Supabase, Streamlit, python-dotenv. Les dépendances `scikit-learn`, `xgboost`, `sweetviz`, `matplotlib` et `altair` sont prévues pour l'analyse et la modélisation des données collectées.

## Sources de données

- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
- [Open-Meteo Weather Forecast API](https://open-meteo.com/en/docs)
