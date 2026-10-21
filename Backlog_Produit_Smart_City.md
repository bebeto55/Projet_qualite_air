# 📋 Backlog Produit Agile — Projet Smart City Qualité de l'Air (Île-de-France)

> **Outils compatibles** : Ce backlog est structuré pour **MS Planner, Trello, Jira, Notion et OneNote** (un fichier d'import direct **`Backlog_Trello_Jira_Planner.csv`** est également fourni à la racine du projet).

---

## 🧭 Vision Produit (Product Vision)

Fournir aux **citoyens, personnes vulnérables, établissements hospitaliers, chercheurs, services municipaux et décideurs publics d'Île-de-France** une plateforme décisionnelle complète permettant de :
1. **Observer** en temps réel (toutes les 30 minutes) et sur l'historique (75 jours) la qualité de l'air et la météo sur **34 stations franciliennes** ;
2. **Anticiper** 24 heures à l'avance (calcul quotidien à **00h45** par Machine Learning **LightGBM**) les épisodes de pollution pour protéger les personnes malades et préparer la logistique hospitalière ;
3. **Cibler** l'impact réel du trafic routier (**Surconcentration Trafic vs Fond de +52 %**, identification de l'**Autoroute A1** comme axe critique) et piloter l'action publique via une **Application Web** et **Power BI**.

---

## 🗂️ Organisation par Epics (Grands Chantiers)

| ID Epic | Nom de l'Epic | Objectif & Plus-Value Utilisateur | Statut |
| :--- | :--- | :--- | :--- |
| **EPIC-01** | **Acquisition & Streaming Multi-Sources (Open-Meteo & 34 Capteurs)** | Capter en continu les 7 polluants, l'indice EAQI et les 5 variables météo sur 34 stations d'Île-de-France (75j d'historique + temps réel 30 min sur VPS). | ✅ Terminé |
| **EPIC-02** | **Stockage Relationnel Cloud & Sécurité (Supabase PostgreSQL)** | Garantir une base de données sans doublon, sécurisée par certificat SSL, sans clé API exposée et gérant 4 rôles utilisateurs. | ✅ Terminé |
| **EPIC-03** | **Modélisation Prédictive IA à 24h (LightGBM) & Google Sheets** | Prédire heure par heure l'AQI des 24 prochaines heures (à 00h45) avec haute précision (MAE = 2,07 pts sur capteur test) et alimenter Google Sheets. | ✅ Terminé |
| **EPIC-04** | **Application Web Interactive (MVP Full-Stack React & FastAPI)** | Offrir 9 onglets opérationnels (Temps réel, Carte 34 stations, Polluants, Mobilité Trafic/Fond, Prévisions 24h, Alertes email, Rapports PDF, Logs). | ✅ Terminé |
| **EPIC-05** | **Business Intelligence & Dashboard Power BI (`Smart_City.pbix`)** | Croiser PostgreSQL (SSL) et Google Sheets (Prévisions 24h) dans 6 pages de tableaux de bord interactifs pour les analystes et décideurs. | ✅ Terminé |
| **EPIC-06** | **Documentation, Livrables, Soutenance & Démo Vidéo** | Produire le README, le rapport complet Word/PDF, la présentation PowerPoint et la démonstration vidéo du MVP. | ✅ Terminé |
| **EPIC-07** | **Améliorations Futures (Backlog V2 — Perspectives)** | Étendre les prévisions à 48h/72h, intégrer le comptage routier temps réel et tester des modèles Deep Learning (LSTM / GNN). | 📌 Planifié (V2) |

---

## 📝 Détail des User Stories par Sprint (Backlog Mis à Jour)

### Sprint 1 — Socle de Données, Historique & Base Cloud (EPIC-01 & EPIC-02)

| ID | User Story (En tant que… Je veux… Afin de…) | Priorité | Points | Statut | Livrable / Critère d'acceptation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **US-01** | **En tant que** data engineer, **je veux** référencer les 34 stations d'Île-de-France (8 trafic, 26 fond) avec leurs coordonnées GPS **afin de** couvrir équitablement toute la région. | Haute (P0) | 3 | ✅ Terminé | Dictionnaire des 34 capteurs validé. |
| **US-02** | **En tant que** chercheur / analyste, **je veux** importer 1 800 heures (75 jours) d'historique Air (EAQI, PM2.5, PM10, NO₂, O₃, SO₂, CO, Pollen) et Météo **afin d'**avoir la profondeur statistique nécessaire au modèle IA. | Haute (P0) | 5 | ✅ Terminé | > 61 000 relevés horaires fusionnés sur le fuseau `Europe/Paris`. |
| **US-03** | **En tant qu'**administrateur, **je veux** stocker les relevés dans Supabase PostgreSQL avec une contrainte d'unicité `(capteur_id, time)` **afin d'**éviter tout doublon lors des synchronisations. | Haute (P0) | 5 | ✅ Terminé | Schéma SQL déployé et insertion idempotente (`upsert`) fonctionnelle. |
| **US-04** | **En tant que** service municipal, **je veux** automatiser la collecte en streaming toutes les 30 minutes sur un serveur distant Linux (VPS via `cron`) **afin que** la base se mette à jour 24h/24 sans intervention humaine. | Haute (P0) | 8 | ✅ Terminé | Tâche `*/30 * * * *` active sur le VPS avec journalisation `HTTP 201 Created`. |

---

### Sprint 2 — Intelligence Artificielle (Prédictions 24h) & Passerelle Cloud (EPIC-03)

| ID | User Story (En tant que… Je veux… Afin de…) | Priorité | Points | Statut | Livrable / Critère d'acceptation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **US-05** | **En tant que** data scientist, **je veux** construire 233 variables explicatives (décalages 1h à 168h, moyennes glissantes, vent vectoriel, météo prévue) **afin de** capturer les « patterns » journaliers et météo. | Haute (P0) | 8 | ✅ Terminé | Pipeline de préparation régularisé sur grille horaire stricte. |
| **US-06** | **En tant que** personne vulnérable ou hôpital, **je veux** disposer de prévisions horaires fiables sur les 24 prochaines heures **afin d'**anticiper les sorties et le matériel médical (masques, oxygène). | Haute (P0) | 13 | ✅ Terminé | 24 modèles LightGBM entraînés ; MAE = 2,07 pts sur capteur test et 5,97 pts sur les 34 stations. |
| **US-07** | **En tant qu'**analyste BI, **je veux** que les prédictions des 24 prochaines heures soient générées chaque nuit à 00h45 et envoyées vers Google Sheets (via certificat Google Workspace) **afin d'**alimenter automatiquement Power BI. | Moyenne (P1) | 5 | ✅ Terminé | Script quotidien planifié à 00h45 et synchronisation Google Sheets opérationnelle. |

---

### Sprint 3 — Application Web Full-Stack (MVP) & Aide à la Décision (EPIC-04)

| ID | User Story (En tant que… Je veux… Afin de…) | Priorité | Points | Statut | Livrable / Critère d'acceptation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **US-08** | **En tant que** citoyen, **je veux** consulter en temps réel l'indice AQI et la carte colorée des 34 stations **afin de** savoir immédiatement si je peux faire du sport ou aérer mon logement. | Haute (P0) | 8 | ✅ Terminé | Onglets *Vue d'ensemble*, *Carte 34 stations* et *Analyse par polluant* réactifs. |
| **US-09** | **En tant qu'**autorité de mobilité, **je veux** comparer les 8 stations routières aux 26 stations de fond **afin de** mesurer la surconcentration (+52 %) et cibler l'axe le plus saturé (Autoroute A1 à 41 %). | Haute (P0) | 5 | ✅ Terminé | Onglet *Mobilité & Trafic* avec indicateurs temps réel et corrélations de Pearson. |
| **US-10** | **En tant qu'**élu local, **je veux** recevoir des alertes automatiques par email en cas de dépassement ou d'anomalie capteur et générer un rapport PDF officiel en 1 clic **afin d'**agir vite en cellule de crise. | Moyenne (P1) | 8 | ✅ Terminé | Onglets *Alertes & Seuils* (détection Z-score + SMTP) et *Rapports PDF*. |
| **US-11** | **En tant que** responsable sécurité, **je veux** une authentification par rôle (*Admin*, *Élu*, *Citoyen*) et un lanceur en 1 clic (`start_smart_city.bat`) **afin de** sécuriser et simplifier l'exploitation du MVP. | Moyenne (P1) | 3 | ✅ Terminé | Authentification JWT active et script de démarrage 1 clic vérifié. |

---

### Sprint 4 — Dashboard Power BI, Rapports & Soutenance (EPIC-05 & EPIC-06)

| ID | User Story (En tant que… Je veux… Afin de…) | Priorité | Points | Statut | Livrable / Critère d'acceptation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **US-12** | **En tant qu'**expert / analyste, **je veux** connecter Power BI à PostgreSQL (via certificat SSL sans clé en clair) et à Google Sheets **afin d'**explorer 6 pages de tableaux de bord croisant Air, Météo et Prévisions 24h. | Haute (P0) | 8 | ✅ Terminé | Fichier `Smart_City.pbix` (6 pages) + assistant SSL intégré à l'application Web. |
| **US-13** | **En tant que** jury / utilisateur, **je veux** disposer d'un `README.md`, d'un rapport Word/PDF complet centré sur la valeur utilisateur et d'une présentation PowerPoint avec démo vidéo **afin d'**évaluer le projet de bout en bout. | Haute (P0) | 5 | ✅ Terminé | `README.md`, `Rapport_Projet_Smart_City_Complet.docx`/`.pdf` et PowerPoint livrés. |

---

### Backlog Futur (V2 — Perspectives d'Amélioration) (EPIC-07)

| ID | User Story (En tant que… Je veux… Afin de…) | Priorité | Points | Statut | Horizon |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **US-14** | **En tant qu'**établissement hospitalier, **je veux** disposer de prédictions étendues à 48h et 72h **afin d'**anticiper encore plus tôt les stocks d'oxygène et de masques. | Moyenne (P2) | 8 | 📌 À faire (V2) | Post-MVP |
| **US-15** | **En tant que** data scientist, **je veux** tester des modèles Deep Learning (LSTM, Transformers, Graph Neural Networks) et intégrer les comptages routiers temps réel **afin d'**améliorer encore la précision des prédictions. | Basse (P3) | 13 | 📌 À faire (V2) | Post-MVP |
