# 🎬 Guide de Soutenance Courte & Scénario de Démo Vidéo Enregistrée

Ce document vous accompagne pour le livrable **« Présentation finale (soutenance courte) avec démo vidéo enregistrée »**, en liant directement votre PowerPoint (**`Air Quality Index (AQI) by Slidesgo.pptx`**) et la démonstration en direct de votre **Prototype fonctionnel (MVP)** et de **Power BI**.

---

## ⏱️ 1. Plan Minuté de la Soutenance Courte (10 minutes)

| Temps | Diapositives PowerPoint | Message Clé (Orienté Plus-Value Utilisateur) |
| :---: | :--- | :--- |
| **00:00 – 02:00** | **Slides 1 à 7** (*Introduction, Pourquoi étudier l'AQI, Échelle & Composants*) | L'air est notre ressource la plus critique (son altération met immédiatement la santé en danger). Notre projet **Smart City** répond à **6 besoins concrets** : prévenir les crises brutales (avertir de rester chez soi), protéger les personnes malades/sensibles, sensibiliser citoyens et industriels, identifier les facteurs d'accroissement/régression, repérer les *patterns* pour anticiper le matériel hospitalier (masques, oxygène), et aider la recherche. |
| **02:00 – 03:30** | **Slides 8 & 9** (*Architecture Globale du Système*) | Présentation du schéma d'architecture : 34 capteurs en Île-de-France (Open-Meteo Air + Météo) → Serveur distant VPS (Streaming toutes les 30 min) → Base Cloud Supabase PostgreSQL → Algorithme IA LightGBM (lancé chaque nuit à 00h45 vers Google Sheets) → Application Web & Power BI au service de 4 profils (*Citoyens, Décideurs, Experts, Services municipaux*). |
| **03:30 – 05:00** | **Slides 10 à 16 & 23–24** (*Collecte 75j, Streaming VPS & Prédiction IA 24h*) | Amorçage historique de 1 800 heures (75 jours) + automatisation `cron` toutes les 30 min sur serveur distant Linux. Prédiction des **24 prochaines heures** par LightGBM : confrontation AQI prédit vs AQI réel très fidèle (**MAE = 2,07 points** sur notre capteur de référence, **5,97 points** sur l'ensemble des 34 stations). |
| **05:00 – 06:00** | **Slides 17 & 18** (*Sécurité Power BI & Google Sheets*) | Sécurité de bout en bout : aucune clé API n'apparaît dans le backend ; Power BI se connecte à PostgreSQL via un **certificat SSL** installé sur la machine et récupère les prévisions 24h depuis **Google Sheets (Google Workspace)** alimenté une fois par jour. |
| **06:00 – 09:00** | **DÉMO VIDÉO / LIVE DU MVP** (*3 minutes — voir scénario ci-dessous*) | Démonstration fluide de l'Application Web et des tableaux de bord Power BI. |
| **09:00 – 10:00** | **Slides 20 à 22** (*Conclusion & Perspectives*) | Réalisation de bout en bout (historique → streaming 30 min → base Cloud → prédictions 24h → Web & Power BI). Perspectives V2 : améliorer encore la précision, étendre l'horizon au-delà de 24h (48h/72h), renforcer la convivialité et tester d'autres algorithmes de Machine Learning. |

---

## 🎥 2. Scénario Pas-à-Pas pour Enregistrer la Démo Vidéo (3 minutes)

> **Astuce avant d'enregistrer** : Lancez `start_smart_city.bat`, ouvrez `http://localhost:5173` dans votre navigateur en plein écran (`F11`), puis lancez l'enregistrement d'écran Windows (**` Touche Windows + Alt + R `** via Xbox Game Bar ou OBS Studio).

### Étape 1 — Connexion par rôle & Vue d'ensemble Temps Réel (0:00 → 0:45)
1. Sur l'écran de connexion, montrez les **3 profils utilisateurs** (*Administrateur*, *Élu / Décideur*, *Citoyen*) et cliquez sur **Connexion Administrateur**.
2. Sur l'onglet **Vue d'ensemble**, montrez le score **European AQI** moyen d'Île-de-France, le polluant majoritaire et les conditions météo.
3. Utilisez le **sélecteur de station** en haut à droite pour choisir une station précise (ex. *Autoroute A1 - Saint-Denis* ou *Paris 1er Les Halles*) : montrez que tous les indicateurs se mettent à jour instantanément pour les habitants de ce quartier.

### Étape 2 — Carte Interactive des 34 Stations & Mobilité / Trafic (0:45 → 1:30)
1. Cliquez sur **Carte des Stations** : survolez quelques marqueurs colorés parmi les 34 capteurs et filtrez entre les stations **Trafic** et les stations **Fond urbain**.
2. Cliquez sur **Mobilité & Trafic** :
   - Montrez l'indicateur **« Surconcentration Trafic vs Fond : +52 % »** (les grands axes routiers ont 52 % de NO₂ en plus que les quartiers résidentiels) ;
   - Montrez l'**« Indice d'Émission Trafic : 41 % (Max : Autoroute A1 Saint-Denis) »** qui indique immédiatement aux autorités quel axe routier doit être régulé en priorité ;
   - Pointez le graphique du cycle diurne (pics à 8h et 19h pour le NO₂, pic à 15h pour l'ozone) qui aide les personnes malades à choisir leur heure de sortie.

### Étape 3 — Prédictions IA à 24 Heures & Alertes Sanitaires (1:30 → 2:15)
1. Cliquez sur **Prédictions IA (24h)** :
   - Montrez la courbe prévue heure par heure pour les **24 prochaines heures** entourée de son **intervalle de confiance à 95 %** ;
   - Expliquez que ce calcul permet aux hôpitaux (masques, oxygène) et à la Préfecture d'anticiper dès la veille.
2. Cliquez sur **Alertes & Seuils** : montrez la détection automatique des dépassements et des anomalies capteurs ainsi que l'envoi d'alertes par email.

### Étape 4 — Power BI (6 Volets) & Rapport PDF Officiel en 1 Clic (2:15 → 3:00)
1. Cliquez sur **Power BI & Analytics** :
   - Parcourez rapidement les **6 volets du rapport `Smart_City`** (*Présentation EAQI*, *Statistiques temporelles*, *Air & Météo*, *Carte à bulles*, *Dernier relevé*, *Prévisions 24h*) et mentionnez le bouton de téléchargement du **Certificat SSL** ;
2. Cliquez sur **Rapports PDF** puis sur **Télécharger le Rapport PDF Officiel** pour conclure sur la prise de décision immédiate pour les élus.
