# 🌍 Smart City — Plateforme Décisionnelle de Surveillance et de Prédiction de la Qualité de l'Air (Île-de-France)

> **« Des données d'aujourd'hui pour une meilleure qualité de l'air demain »**  
> **Dépôt GitHub officiel :** [https://github.com/bebeto55/Projet_qualite_air](https://github.com/bebeto55/Projet_qualite_air) *(Branche principale : **`main`** — [Voir les branches](https://github.com/bebeto55/Projet_qualite_air/branches))*

---

## 🎯 1. Ce que fait l'application (Objectifs & Plus-Value Utilisateur)

Cette plateforme répond à un enjeu majeur de santé publique en Île-de-France : transformer les mesures environnementales et météorologiques en **informations claires, préventives et directement exploitables** :

1. **Prévenir les crises sanitaires et protéger les personnes vulnérables** : Avertir à temps les habitants (asthmatiques, insuffisants respiratoires, enfants, seniors) en cas de dégradation brutale ou prévue de l'indice de qualité de l'air (**European AQI**).
2. **Anticiper 24 heures à l'avance (IA LightGBM)** : Prédire heure par heure l'évolution de l'indice AQI sur les **24 prochaines heures** (calcul automatisé chaque nuit à **00h45**, avec une erreur moyenne **MAE de 2,07 points** sur le capteur de référence et **5,97 points** sur les 34 stations) afin de permettre aux hôpitaux d'anticiper leurs équipements (masques, oxygène) et aux autorités de déclencher les mesures de régulation routière à temps.
3. **Cibler la responsabilité du trafic routier** : Comparer en temps réel **8 stations de trafic routier** (Autoroute A1, Périphérique, Opéra, Champs-Élysées, Victor Basch, RN6, RN20...) et **26 stations de fond urbain et rural** pour mesurer la **Surconcentration Trafic vs Fond (+52 % de NO₂)** et l'**Indice d'Émission Trafic (41 % — Point critique : Autoroute A1 à Saint-Denis)**.
4. **Sensibiliser et éclairer la décision publique (Web + Power BI)** : Offrir une **Application Web interactive à 9 onglets** couplée à un rapport **Microsoft Power BI à 6 volets (`Smart_City.pbix`)**, un **Dashboard de Données PDF (`Dashboard_Donnees_Smart_City.pdf`)** et un **générateur de bilans officiels PDF en 1 clic** pour les élus et chercheurs.

---

## 🏗️ 2. Architecture du Système

L'architecture de bout en bout s'articule autour de **5 briques principales** :

1. **Sources de données (Open-Meteo Air & Météo + 34 capteurs Île-de-France)** :
   - **Qualité de l'air (CAMS)** : European AQI, PM10, PM2.5, NO₂, O₃, SO₂, CO, Pollen de bouleau.
   - **Météorologie** : Température (2 m), Humidité relative, Vent (vitesse et direction à 10 m), Précipitations.
2. **Ingestion & Traitement continu (Serveur distant VPS Linux sans Docker)** :
   - **Amorçage historique** : 1 800 heures (75 jours complets, > 61 000 relevés horaires).
   - **Streaming temps réel** : Collecte, nettoyage, fusion Air + Météo et envoi vers le Cloud **toutes les 30 minutes** via tâche planifiée (`cron`).
3. **Base de données Cloud (Supabase PostgreSQL)** :
   - Stockage relationnel sécurisé (certificat SSL, déduplication native sur `(capteur_id, time)`), gestion des utilisateurs et des rôles (*Citoyens*, *Décideurs / Autorités*, *Experts / Analystes*, *Services municipaux*).
4. **Moteur de Machine Learning (LightGBM 24 horizons) & Google Sheets** :
   - Exécution quotidienne à **00h45** : ingénierie de 233 variables (mémoire des polluants jusqu'à 7 jours, composantes du vent, prévisions météo futures) et sauvegarde automatique des prédictions 24h dans **Google Sheets (Google Workspace)**.
5. **Restitution : Application Web (React 19 + FastAPI) & Power BI** :
   - Portail Web interactif (9 onglets) + Tableaux de bord **Power BI** connectés en SSL à PostgreSQL et au Google Sheets des prévisions 24h.

---

## 🚀 3. Comment récupérer et lancer l'application

### Étape 0 — Cloner le dépôt GitHub (branche `main`)
```bash
git clone -b main https://github.com/bebeto55/Projet_qualite_air.git
cd Projet_qualite_air
```

### Option A — Lancement rapide en 1 clic (Windows)

Double-cliquez sur le fichier **`start_smart_city.bat`** à la racine du projet (ou lancez-le depuis un terminal) :
```bat
.\start_smart_city.bat
```
Ce script démarre automatiquement :
- Le **serveur Backend API (FastAPI)** sur `http://localhost:8000` (Documentation Swagger sur `http://localhost:8000/docs`) ;
- Le **portail Frontend Web (React / Vite)** sur `http://localhost:5173`.

---

### Option B — Lancement manuel dans deux terminaux

#### 1. Démarrer le Backend (API FastAPI & Moteur IA)
```powershell
cd Back\api
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*(Si l'environnement virtuel n'est pas encore créé : `python -m venv .venv` puis `.\.venv\Scripts\pip install -r requirements.txt`).*

#### 2. Démarrer le Frontend (Interface Web React)
```powershell
cd frontend
npm install
npm run dev
```
Ouvrez ensuite votre navigateur sur **`http://localhost:5173`**.

---

## 🔐 4. Comptes de démonstration (Authentification par Rôle)

Sur l'écran de connexion (`http://localhost:5173`), vous pouvez utiliser les boutons de connexion rapide en 1 clic ou saisir :

| Rôle Utilisateur | Identifiant | Mot de passe | Droits & Fonctionnalités |
| :--- | :--- | :--- | :--- |
| **Administrateur / Services municipaux** | `admin` | `admin123` | Accès complet : 9 onglets, rafraîchissement manuel des capteurs, configuration des seuils d'alerte, logs système, rapports PDF, Power BI. |
| **Décideur / Élu local** | `elu` | `elu123` | Tableaux de bord décisionnels, carte des 34 stations, analyse Mobilité/Trafic, prévisions 24h, Power BI et génération de rapports PDF officiels. |
| **Citoyen / Usager** | `citoyen` | `citoyen123` | Consultation temps réel par commune, carte interactive, prévisions 24h et recommandations sanitaires (sport, aération, pollens). |

---

## 📊 5. Ouvrir le Dashboard Power BI (`Smart_City.pbix`) & le Dashboard de Données PDF

1. **Outil BI interactif** : Ouvrez **`Smart_City.pbix`** dans **Microsoft Power BI Desktop** (ou consultez directement l'onglet **« Power BI & Analytics »** intégré dans l'application Web).
2. **Exemple en PDF** : Consultez **`Dashboard_Donnees_Smart_City.pdf`** qui présente les 6 planches analytiques du Dashboard de données (Synthèse régionale EAQI, Évolution temporelle & Moyenne mobile, Matrice Air × Météo, Cartographie des 34 stations, Mobilité Trafic vs Fond +52 %, et Prévisions IA à 24 heures).
3. **Configuration SSL PostgreSQL (Supabase)** :
   - Dans l'onglet **Power BI & Analytics** de l'application Web, cliquez sur **« Télécharger Certificat SSL (.crt) »** ;
   - Installez le certificat dans *Autorités de certification racines de confiance* sous Windows ;
   - Aucune clé API n'est stockée en clair dans le code.

---

## 📦 6. Récapitulatif des 6 Livrables Officiels du Projet

| Livrable demandé | Emplacement / Lien officiel | Description |
| :--- | :--- | :--- |
| **1. Prototype fonctionnel (MVP)** | `Back/api/` + `frontend/` + `start_smart_city.bat` | Application Web Full-Stack (9 onglets) connectée à Supabase PostgreSQL et au modèle IA LightGBM 24h. |
| **2. Backlog produit mis à jour** | `Backlog_Produit_Smart_City.md` & `Backlog_Trello_Jira_Planner.csv` | Backlog Agile complet (Epics, User Stories, Priorités, Statuts) prêt à importer dans Trello, Jira, MS Planner ou Notion. |
| **3. Code source (GitHub)** | [https://github.com/bebeto55/Projet_qualite_air](https://github.com/bebeto55/Projet_qualite_air) *(branche `main`)* | Code source complet et structuré sur la branche `main` du dépôt GitHub officiel. |
| **4. Documentation minimale** | `README.md` (ce fichier) | Guide d'architecture, fonctionnalités et instructions de lancement pas à pas. |
| **5. Dashboard ou rapport de données** | `Smart_City.pbix` + `Dashboard_Donnees_Smart_City.pdf` + `Rapport_Projet_Smart_City_Complet.docx` / `.pdf` | Dashboard Power BI (6 volets), Dashboard de données illustré en PDF, et Rapport complet du projet en Word et PDF. |
| **6. Présentation finale & Démo** | `Air Quality Index (AQI) by Slidesgo.pptx` + `Guide_Soutenance_et_Demo_Video.md` | Support de présentation PowerPoint et scénario minuté pour la démonstration vidéo. |
