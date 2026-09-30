# Projet qualité de l'air

## Présentation

Ce projet analyse la qualité de l'air et génère une **prédiction pour le lendemain**.

Les données utilisées comprennent des variables météorologiques et des indicateurs de qualité de l'air.

### Variables météorologiques

| Variable | Description | Unité |
|---|---|---|
| `temperature_2m` | Température à 2 mètres | °C |
| `relative_humidity_2m` | Humidité relative à 2 mètres | % |
| `wind_speed_10m` | Vitesse du vent à 10 mètres | km/h |
| `wind_direction_10m` | Direction du vent à 10 mètres (0° = Nord) | degrés |
| `precipitation` | Précipitations | mm |

---

## Fonctionnement général

```text
APIs de données
      │
      ▼
Récupération des données
      │
      ├── Données historiques ──► import_historique.py ──┐
      │                                                  │
      └── Nouvelles données ───► chargement_streaming.py ┤
                                                         ▼
                                                     Supabase
                                                         │
                                                         ▼
                                            Analyse / Machine Learning
                                                         │
                                                         ▼
                                             Prédiction pour le lendemain
```

---

## Installation et configuration

### 1. Token de l'API World Air Quality Index (WAQI)

1. Créer un token sur : <https://aqicn.org/data-platform/token/>
2. À la racine du projet, créer le dossier `.streamlit`, puis le fichier `secrets.toml` à l'intérieur.
3. Ajouter dans `secrets.toml` :

   ```toml
   WQAI_token = "votre_token"
   ```

Structure attendue :

```text
projet/
├── .streamlit/
│   └── secrets.toml
├── ...
```

> ⚠️ **Sécurité** : `secrets.toml` contient des informations sensibles. Ne le publiez **jamais** sur GitHub : ajoutez `.streamlit/secrets.toml` à votre `.gitignore`.

### 2. Sweetviz (si nécessaire)

Si Sweetviz n'est pas installé, décommenter la ligne suivante dans le notebook, puis exécuter la cellule :

```python
!pip install sweetviz
```

---

## Lancement du programme

### 1. Installer les dépendances

Deux scripts installent automatiquement les dépendances. Il est recommandé de les exécuter avant le reste du projet :

| Script | Rôle |
|---|---|
| `1-launcher_for_BD_1.py` | Dépendances pour la récupération et la gestion des données |
| `2-launcher_for_algo.py` | Dépendances pour les algorithmes de machine learning |

### 2. Créer la base de données Supabase

1. Créer un nouveau projet sur <https://supabase.com/>.
2. Ouvrir le **SQL Editor** de Supabase.
3. Exécuter, dans l'ordre, le contenu des fichiers :
   1. `1-autorisation.sql` : configuration des autorisations
   2. `2-table.sql` : création des tables du projet

### 3. Charger les données historiques

1. Récupérer dans Supabase :
   - l'**URL** du projet ;
   - la **clé API publique** nécessaire à la connexion.
2. Renseigner ces informations dans `import_historique.py`, dans la section de configuration située juste avant la fonction `envoyer_dataframe()`.
3. Exécuter le script :

   ```bash
   python import_historique.py
   ```

> 💡 Idéalement, stockez la clé API dans les secrets Streamlit (`.streamlit/secrets.toml`), comme le token WAQI.

### 4. Charger les données en continu

Une fois l'historique chargé, lancer :

```bash
python chargement_streaming.py
```

Ce script tourne en continu : il récupère régulièrement les nouvelles données et les ajoute à Supabase.

**Gestion des doublons** : ils sont contrôlés à partir du couple `capteur_id` + `time`. Une donnée déjà présente dans la base n'est pas ajoutée une seconde fois.

---

## Résumé : ordre d'exécution

1. Configurer le token WAQI dans `.streamlit/secrets.toml`.
2. Installer Sweetviz si nécessaire.
3. Exécuter `1-launcher_for_BD_1.py`.
4. Exécuter `2-launcher_for_algo.py`.
5. Créer le projet Supabase.
6. Exécuter `1-autorisation.sql` dans le SQL Editor.
7. Exécuter `2-table.sql` dans le SQL Editor.
8. Configurer l'URL et la clé API Supabase dans `import_historique.py`.
9. Exécuter `import_historique.py` pour charger l'historique.
10. Exécuter `chargement_streaming.py` pour alimenter la base en continu.
11. Lancer les notebooks/scripts d'analyse et de prédiction.