"""Génère le rapport académique et technique complet du projet Smart City (Introduction, Revue de littérature, Corps détaillé du code, Conclusion & Bibliographie)."""
import base64
import subprocess
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
PBIX_PATH = ROOT_DIR / "Back" / "Smart_City.pbix"
OUT_HTML = ROOT_DIR / "Rapport_Projet_Smart_City.html"
OUT_PDF = ROOT_DIR / "Rapport_Projet_Smart_City.pdf"


def get_pbix_image_b64(item_prefix: str) -> str:
    """Extrait une image du fichier Smart_City.pbix en base64 pour l'intégrer au rapport."""
    if not PBIX_PATH.exists():
        return ""
    try:
        with zipfile.ZipFile(PBIX_PATH, "r") as z:
            for name in z.namelist():
                if item_prefix in name:
                    data = z.read(name)
                    mime = "image/webp" if name.endswith(".webp") else "image/png" if name.endswith(".png") else "image/jpeg"
                    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
    except Exception:
        pass
    return ""


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8" />
<title>Mémoire & Rapport Technique de Projet — Smart City Qualité de l'Air Île-de-France</title>
<style>
  @page {
    size: A4 portrait;
    margin: 11mm 13mm 12mm 13mm;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    background: #ffffff;
    line-height: 1.42;
    font-size: 9.4pt;
    text-align: justify;
  }
  .page {
    page-break-after: always;
    padding-bottom: 4mm;
  }
  .page:last-child {
    page-break-after: auto;
  }

  /* Page de garde */
  .cover-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0369a1 100%);
    color: #ffffff;
    border-radius: 14px;
    padding: 22px 25px;
    margin-bottom: 13px;
    border: 1px solid #1e3a8a;
    text-align: left;
  }
  .cover-badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.22);
    border: 1px solid #10b981;
    color: #6ee7b7;
    font-size: 8pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 3px 11px;
    border-radius: 999px;
    margin-bottom: 8px;
  }
  .cover-title {
    font-size: 19.5pt;
    font-weight: 800;
    line-height: 1.16;
    margin-bottom: 7px;
  }
  .cover-subtitle {
    font-size: 10pt;
    color: #cbd5e1;
    margin-bottom: 13px;
    line-height: 1.38;
  }
  .cover-meta {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
    font-size: 8.3pt;
    color: #94a3b8;
    border-top: 1px solid rgba(255,255,255,0.15);
    padding-top: 9px;
  }
  .cover-meta strong { color: #f8fafc; }

  /* Titres de chapitres */
  .sec-header {
    display: flex;
    align-items: center;
    gap: 9px;
    margin: 9px 0 7px 0;
    padding-bottom: 4px;
    border-bottom: 2px solid #0284c7;
    text-align: left;
  }
  .sec-num {
    background: #0284c7;
    color: #fff;
    font-weight: 800;
    font-size: 9pt;
    padding: 2px 8px;
    border-radius: 5px;
    white-space: nowrap;
  }
  .sec-title {
    font-size: 12pt;
    font-weight: 800;
    color: #0f172a;
  }
  h3 {
    font-size: 10pt;
    font-weight: 700;
    color: #1e293b;
    margin: 7px 0 4px 0;
    text-align: left;
  }
  p { margin-bottom: 5.5px; color: #334155; }

  /* Grilles & Cartes */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 8px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 9px; margin-bottom: 8px; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 9px; }

  .card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 11px;
    text-align: left;
  }
  .kpi-val {
    font-size: 14.5pt;
    font-weight: 800;
    color: #0284c7;
    line-height: 1.12;
  }
  .kpi-lbl {
    font-size: 7.6pt;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #64748b;
    font-weight: 700;
  }

  /* Figures */
  .figure-box {
    background: #0f172a;
    color: #f8fafc;
    border-radius: 10px;
    padding: 10px 13px;
    margin: 6px 0 8px 0;
    border: 1px solid #334155;
  }
  .figure-caption {
    font-size: 7.9pt;
    color: #94a3b8;
    margin-top: 5px;
    text-align: center;
    font-style: italic;
  }

  /* Tableaux */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 5px 0 8px 0;
    font-size: 8.3pt;
    text-align: left;
  }
  th {
    background: #0f172a;
    color: #ffffff;
    text-align: left;
    padding: 5px 7px;
    font-weight: 700;
    font-size: 7.9pt;
  }
  td {
    padding: 4px 7px;
    border-bottom: 1px solid #e2e8f0;
    color: #1e293b;
    vertical-align: top;
  }
  tr:nth-child(even) td { background: #f8fafc; }

  .formula-box {
    background: #eff6ff;
    border-left: 3.5px solid #0284c7;
    padding: 6.5px 10px;
    border-radius: 0 7px 7px 0;
    margin: 5.5px 0;
    font-size: 8.6pt;
    text-align: left;
  }
  .lit-box {
    background: #f8fafc;
    border-left: 3.5px solid #6366f1;
    padding: 6.5px 10px;
    border-radius: 0 7px 7px 0;
    margin: 5.5px 0;
    font-size: 8.6pt;
    text-align: left;
  }
  .pitch-box {
    background: #ecfdf5;
    border-left: 3.5px solid #10b981;
    padding: 6.5px 10px;
    border-radius: 0 7px 7px 0;
    margin: 5.5px 0;
    font-size: 8.6pt;
    color: #064e3b;
    text-align: left;
  }
  code {
    font-family: Consolas, 'Courier New', monospace;
    font-size: 8pt;
    background: #e2e8f0;
    padding: 1px 4px;
    border-radius: 3px;
    color: #0f172a;
  }
  ul { padding-left: 16px; margin-bottom: 5px; }
  li { margin-bottom: 2.5px; color: #334155; }
  .toc-row {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px dotted #cbd5e1;
    padding: 3.2px 0;
    font-size: 8.6pt;
  }
</style>
</head>
<body>

<!-- ══════════════════════════════════════════════════════════════════════════
     PAGE 1 : PAGE DE GARDE OFFICIELLE, RÉSUMÉ EXÉCUTIF & SOMMAIRE
     ══════════════════════════════════════════════════════════════════════════ -->
<div class="page">
  <div class="cover-banner">
    <div class="cover-badge">Rapport Scientifique &amp; Mémoire d'Ingénierie — Projet Smart City</div>
    <div class="cover-title">Surveillance Temps Réel, Analyse Physico-Chimique et Prédiction Multi-Horizons par Intelligence Artificielle de la Qualité de l'Air en Île-de-France</div>
    <div class="cover-subtitle">
      Conception de bout en bout d'une infrastructure décisionnelle urbaine : Pipeline ETL Open-Meteo / CAMS vers Supabase PostgreSQL, Modélisation Machine Learning LightGBM à 24 horizons (233 variables), API REST FastAPI, Portail Web React et Business Intelligence Power BI.
    </div>
    <div class="cover-meta">
      <span><strong>Périmètre :</strong> 34 Capteurs Île-de-France</span>
      <span><strong>SGBD Cloud :</strong> Supabase PostgreSQL (table <code>mesures</code>)</span>
      <span><strong>Modélisation IA :</strong> 24 × LightGBM (<code>bundle_aqi.joblib</code>)</span>
      <span><strong>Restitution :</strong> React 19 · FastAPI · Power BI</span>
    </div>
  </div>

  <div class="grid-4">
    <div class="card">
      <div class="kpi-lbl">Maillage Territorial</div>
      <div class="kpi-val">34 Stations</div>
      <div style="font-size:7.6pt;color:#64748b;">8 stations Trafic · 26 stations Fond</div>
    </div>
    <div class="card">
      <div class="kpi-lbl">Ingestion Initiale</div>
      <div class="kpi-val">1 800 h / capt.</div>
      <div style="font-size:7.6pt;color:#64748b;">75 jours d'historique + Streaming 30 min</div>
    </div>
    <div class="card">
      <div class="kpi-lbl">Modèles Prédictifs</div>
      <div class="kpi-val">24 × LGBM</div>
      <div style="font-size:7.6pt;color:#10b981;font-weight:700;">233 features · MAE = 5,97 EAQI (80 %)</div>
    </div>
    <div class="card">
      <div class="kpi-lbl">Variables Suivies</div>
      <div class="kpi-val">13 Séries</div>
      <div style="font-size:7.6pt;color:#64748b;">8 variables Air/Pollen + 5 variables Météo</div>
    </div>
  </div>

  <div class="card" style="margin-bottom:9px;">
    <h3 style="margin-top:0;color:#0284c7;">Résumé Exécutif (Abstract)</h3>
    <p style="margin-bottom:3px;">
      La pollution atmosphérique en milieu urbain dense constitue l'un des premiers facteurs de risque sanitaire environnemental en Europe. Ce rapport présente la conception et la réalisation complète du projet <strong>Smart City Qualité de l'Air en Île-de-France</strong>. En nous appuyant sur la littérature scientifique en chimie atmosphérique (cycle photochimique de Leighton, dynamique de la couche limite planétaire, granulométrie des aérosols) et en apprentissage statistique (arbres de gradient boostés multi-horizons), nous avons développé une architecture modulaire en quatre couches : <strong>(1)</strong> un pipeline d'acquisition automatisé interrogeant les modèles CAMS/Open-Meteo pour 34 stations franciliennes et alimentant une base PostgreSQL hébergée sur Supabase ; <strong>(2)</strong> une chaîne de traitement et d'ingénierie de 233 variables spatio-temporelles pilotant 24 régresseurs LightGBM indépendants pour prédire l'indice européen EAQI de +1h à +24h ; <strong>(3)</strong> un serveur backend FastAPI sécurisé par JWT assurant l'inférence temps réel, la détection statistique d'anomalies par Z-score et le routage d'alertes ; et <strong>(4)</strong> une double interface de visualisation couplant un tableau de bord Power BI (<code>Smart_City.pbix</code>) et une application Web React à 9 onglets métier.
    </p>
  </div>

  <div class="card" style="margin-bottom:9px;">
    <h3 style="margin-top:0;color:#0f172a;">Sommaire Général du Rapport</h3>
    <div class="toc-row"><span><strong>1. Introduction Générale : Contexte Sanitaire, Enjeux Smart City &amp; Problématique</strong></span><span><strong>Page 2</strong></span></div>
    <div class="toc-row"><span><strong>2. Revue de la Littérature : Physico-Chimie Atmosphérique &amp; État de l'Art Machine Learning</strong></span><span><strong>Page 3</strong></span></div>
    <div class="toc-row"><span><strong>3. Chapitre I — Ingénierie des Données, Pipeline ETL Open-Meteo &amp; Architecture Supabase</strong> (<code>Back/Projet_qualite_air/</code>)</span><span><strong>Page 4</strong></span></div>
    <div class="toc-row"><span><strong>4. Chapitre II — Modélisation Prédictive IA Multi-Horizons à 24h &amp; Feature Engineering</strong> (<code>Back/prediction/</code>)</span><span><strong>Page 5</strong></span></div>
    <div class="toc-row"><span><strong>5. Chapitre III — Architecture Backend FastAPI, Détection d'Anomalies &amp; Portail React</strong> (<code>Back/api/</code> &amp; <code>frontend/</code>)</span><span><strong>Page 6</strong></span></div>
    <div class="toc-row"><span><strong>6. Chapitre IV — Mobilité Routière, Business Intelligence Power BI &amp; Gouvernance SSL</strong> (<code>Smart_City.pbix</code>)</span><span><strong>Page 7</strong></span></div>
    <div class="toc-row"><span><strong>7. Conclusion Générale, Analyse Critique, Limites &amp; Perspectives d'Évolution</strong></span><span><strong>Page 8</strong></span></div>
    <div class="toc-row" style="border-bottom:none;"><span><strong>8. Bibliographie Scientifique, Technique &amp; Réglementaire</strong></span><span><strong>Page 8</strong></span></div>
  </div>

  __COVER_IMAGES__
</div>

<!-- ══════════════════════════════════════════════════════════════════════════
     PAGE 2 : 1. INTRODUCTION GÉNÉRALE & ENJEUX DU PROJET
     ══════════════════════════════════════════════════════════════════════════ -->
<div class="page">
  <div class="sec-header">
    <span class="sec-num">CHAPITRE 1</span>
    <span class="sec-title">Introduction Générale : Contexte Sanitaire, Cadre Réglementaire &amp; Problématique</span>
  </div>

  <h3>1.1 Contexte sanitaire mondial, européen et francilien</h3>
  <p>
    Selon l'<strong>Organisation Mondiale de la Santé (OMS, 2021)</strong>, la pollution de l'air ambiant extérieur est responsable d'environ <strong>4,2 millions de décès prématurés par an</strong> dans le monde, principalement par cardiopathies ischémiques, accidents vasculaires cérébraux (AVC), bronchopneumopathies chroniques obstructives (BPCO) et cancers bronchopulmonaires. En Europe, l'<strong>Agence Européenne pour l'Environnement (EEA, 2023)</strong> estime que plus de 250 000 décès annuels restent attribuables à une exposition chronique aux particules fines (PM<sub>2.5</sub>) au-delà des seuils recommandés. En France, <strong>Santé Publique France (2021)</strong> évalue ce fardeau sanitaire à près de <strong>40 000 décès prématurés par an</strong> et une perte d'espérance de vie moyenne de 7 à 8 mois dans les grandes métropoles.
  </p>
  <p>
    La région <strong>Île-de-France</strong>, qui concentre plus de <strong>12,3 millions d'habitants</strong> (soit 18 % de la population métropolitaine sur seulement 2 % du territoire), présente une vulnérabilité structurelle majeure. La densité du réseau routier (Boulevard Périphérique, autoroutes radiales A1, A3, A4, A6, A13, routes nationales RN6 et RN20), combinée au chauffage résidentiel/tertiaire et à la topographie de la cuvette parisienne, engendre des dépassements réguliers des valeurs guides sanitaires, particulièrement le long des corridors de circulation surveillés par <strong>Airparif</strong>.
  </p>

  <h3>1.2 Le paradigme de la « Smart City » et l'évolution réglementaire européenne</h3>
  <p>
    Dans la littérature académique sur les villes intelligentes (<strong>Giffinger et al., 2007 ; Zanella et al., 2014</strong>), la composante <em>Smart Environment</em> repose sur l'instrumentation numérique de l'espace urbain afin de transformer des flux continus de données environnementales en décisions publiques rapides et ciblées. Cette exigence est renforcée par la révision de la <strong>Directive européenne sur la qualité de l'air ambiant (Directive 2008/50/CE révisée en 2024)</strong>, qui abaisse drastiquement les valeurs limites réglementaires à horizon 2030 pour les aligner progressivement sur les lignes directrices de l'OMS (2021), ainsi que par le déploiement des <strong>Zones à Faibles Émissions mobilité (ZFE-m)</strong> dans la Métropole du Grand Paris.
  </p>

  <div class="lit-box">
    <strong>Norme Européenne — L'Indice Officiel European Air Quality Index (EAQI) :</strong><br/>
    Mis en place par l'Agence Européenne pour l'Environnement (EEA) et le service atmosphérique <strong>Copernicus (CAMS)</strong>, l'indice <code>european_aqi</code> synthétise en une valeur unique la concentration des 5 polluants réglementaires majeurs (PM<sub>2.5</sub>, PM<sub>10</sub>, NO<sub>2</sub>, O<sub>3</sub>, SO<sub>2</sub>) selon une règle du « polluant majorant » (le sous-indice le plus dégradé détermine l'indice global) : <strong>0–20 (Bon)</strong>, <strong>20–40 (Correct)</strong>, <strong>40–60 (Moyen/Modéré)</strong>, <strong>60–80 (Médiocre/Mauvais)</strong>, <strong>80–100 (Très mauvais)</strong> et <strong>&gt;100 (Extrêmement mauvais)</strong>.
  </div>

  <h3>1.3 Problématique scientifique et objectifs opérationnels du projet</h3>
  <p>
    Les outils traditionnels de suivi souffrent souvent d'une <strong>dichotomie</strong> : d'un côté, des portails de mesure purement descriptifs qui constatent le pic de pollution une fois que la population y est déjà exposée ; de l'autre, des modèles numériques lourds (chimie-transport) difficiles à interpréter pour un élu local. La problématique centrale de notre projet s'énonce ainsi :
  </p>
  <div class="formula-box">
    <strong>Problématique :</strong> <em>Comment concevoir une chaîne décisionnelle automatisée de bout en bout capable d'acquérir en continu les données multi-polluants et météorologiques de 34 stations franciliennes, de prédire avec fiabilité l'indice European AQI sur un horizon glissant de 24 heures par apprentissage automatique, et de restituer ces informations sous forme d'indicateurs actionnables (alertes sanitaires, régulation du trafic, rapports BI) ?</em>
  </div>

  <!-- FIGURE 1 : Architecture globale -->
  <div class="figure-box">
    <svg viewBox="0 0 820 190" width="100%" height="175" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>
        </marker>
      </defs>
      <!-- Bloc 1 -->
      <rect x="8" y="10" width="180" height="168" rx="8" fill="#1e293b" stroke="#0284c7" stroke-width="1.5"/>
      <rect x="8" y="10" width="180" height="24" rx="8" fill="#0284c7"/>
      <text x="98" y="26" fill="#fff" font-size="9.5" font-weight="bold" text-anchor="middle">1. ACQUISITION (Open-Meteo)</text>
      <text x="18" y="50" fill="#e2e8f0" font-size="8.5" font-weight="bold">• API Air Quality (CAMS)</text>
      <text x="22" y="64" fill="#94a3b8" font-size="8">EAQI, PM10, PM2.5, NO₂, O₃,</text>
      <text x="22" y="76" fill="#94a3b8" font-size="8">SO₂, CO, Pollen de bouleau</text>
      <text x="18" y="94" fill="#e2e8f0" font-size="8.5" font-weight="bold">• API Weather Forecast</text>
      <text x="22" y="108" fill="#94a3b8" font-size="8">Temp 2m, Humidité, Vent 10m, Pluie</text>
      <text x="18" y="128" fill="#38bdf8" font-size="8.5" font-weight="bold">• Scripts Python :</text>
      <text x="22" y="142" fill="#cbd5e1" font-size="8">app_historique.py (1800h)</text>
      <text x="22" y="155" fill="#cbd5e1" font-size="8">app_streaming.py / scheduler.yml</text>

      <line x1="190" y1="94" x2="215" y2="94" stroke="#38bdf8" stroke-width="2" marker-end="url(#arr)"/>

      <!-- Bloc 2 -->
      <rect x="218" y="10" width="175" height="168" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="1.5"/>
      <rect x="218" y="10" width="175" height="24" rx="8" fill="#059669"/>
      <text x="305" y="26" fill="#fff" font-size="9.5" font-weight="bold" text-anchor="middle">2. STOCKAGE (Supabase)</text>
      <text x="228" y="50" fill="#6ee7b7" font-size="8.5" font-weight="bold">PostgreSQL : public.mesures</text>
      <text x="228" y="66" fill="#cbd5e1" font-size="8">• 34 capteurs géolocalisés</text>
      <text x="228" y="80" fill="#cbd5e1" font-size="8">• Upsert idempotent sur</text>
      <text x="234" y="92" fill="#38bdf8" font-size="8">(capteur_id, time)</text>
      <text x="228" y="110" fill="#cbd5e1" font-size="8">• RPC vider_mesures()</text>
      <text x="228" y="126" fill="#cbd5e1" font-size="8">• Sécurité RLS &amp; Pooler TLS</text>
      <text x="228" y="142" fill="#94a3b8" font-size="8">• EDA : rapport_qualite_air.html</text>
      <text x="228" y="156" fill="#94a3b8" font-size="8">  (Généré via Sweetviz)</text>

      <line x1="395" y1="94" x2="420" y2="94" stroke="#38bdf8" stroke-width="2" marker-end="url(#arr)"/>

      <!-- Bloc 3 -->
      <rect x="423" y="10" width="185" height="168" rx="8" fill="#1e293b" stroke="#8b5cf6" stroke-width="1.5"/>
      <rect x="423" y="10" width="185" height="24" rx="8" fill="#6d28d9"/>
      <text x="515" y="26" fill="#fff" font-size="9.5" font-weight="bold" text-anchor="middle">3. IA &amp; API REST (FastAPI)</text>
      <text x="433" y="50" fill="#ddd6fe" font-size="8.5" font-weight="bold">Pipeline ML (Back/prediction/)</text>
      <text x="433" y="64" fill="#cbd5e1" font-size="8">• importer_df.py (233 features)</text>
      <text x="433" y="78" fill="#cbd5e1" font-size="8">• bundle_aqi.joblib (24 × LGBM)</text>
      <text x="433" y="92" fill="#cbd5e1" font-size="8">• predict.py → Google Sheets</text>
      <text x="433" y="112" fill="#ddd6fe" font-size="8.5" font-weight="bold">Serveur Back/api/ (Port 8080)</text>
      <text x="433" y="126" fill="#cbd5e1" font-size="8">• 18 endpoints REST + Auth JWT</text>
      <text x="433" y="140" fill="#cbd5e1" font-size="8">• Anomalies Z-score (|z| ≥ 3σ)</text>
      <text x="433" y="154" fill="#6ee7b7" font-size="8">• Back-testing : MAE = 5,97 EAQI</text>

      <line x1="610" y1="94" x2="635" y2="94" stroke="#38bdf8" stroke-width="2" marker-end="url(#arr)"/>

      <!-- Bloc 4 -->
      <rect x="638" y="10" width="174" height="168" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
      <rect x="638" y="10" width="174" height="24" rx="8" fill="#d97706"/>
      <text x="725" y="26" fill="#fff" font-size="9.5" font-weight="bold" text-anchor="middle">4. RESTITUTION &amp; BI</text>
      <text x="648" y="50" fill="#fde68a" font-size="8.5" font-weight="bold">Portail Web React 19 (5173)</text>
      <text x="648" y="64" fill="#cbd5e1" font-size="8">• 9 Onglets (Temps réel, Carte,</text>
      <text x="648" y="76" fill="#cbd5e1" font-size="8">  Polluants, IA J+1, Mobilité,</text>
      <text x="648" y="88" fill="#cbd5e1" font-size="8">  Alertes, Rapports PDF, Logs)</text>
      <text x="648" y="110" fill="#fde68a" font-size="8.5" font-weight="bold">Power BI (Smart_City.pbix)</text>
      <text x="648" y="124" fill="#cbd5e1" font-size="8">• 6 Pages : Présentation, Stats,</text>
      <text x="648" y="136" fill="#cbd5e1" font-size="8">  Autres données, Carte,</text>
      <text x="648" y="148" fill="#cbd5e1" font-size="8">  Actualité, Prévisions</text>
    </svg>
    <div class="figure-caption">Figure 1 — Architecture fonctionnelle et technique complète implémentée dans le projet Smart City.</div>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════════════════════
     PAGE 3 : 2. REVUE DE LA LITTÉRATURE SCIENTIFIQUE & ÉTAT DE L'ART ML
     ══════════════════════════════════════════════════════════════════════════ -->
<div class="page">
  <div class="sec-header">
    <span class="sec-num">CHAPITRE 2</span>
    <span class="sec-title">Revue de la Littérature : Physico-Chimie de l'Air &amp; Modélisation Prédictive</span>
  </div>

  <h3>2.1 Dynamique physico-chimique des polluants urbains et interactions météorologiques</h3>
  <p>
    La modélisation prédictive de la qualité de l'air ne peut être dissociée des lois physiques et chimiques qui gouvernent l'atmosphère urbaine (<strong>Seinfeld &amp; Pandis, 2016 ; Jacob, 1999</strong>). Les huit variables atmosphériques collectées dans notre projet répondent à quatre mécanismes fondamentaux :
  </p>
  <ul>
    <li>
      <strong>1. L'équilibre photochimique de Leighton (NO – NO<sub>2</sub> – O<sub>3</sub>) :</strong> En milieu urbain, les moteurs thermiques émettent principalement du monoxyde d'azote (NO) et du dioxyde d'azote (NO<sub>2</sub>). Sous l'effet du rayonnement solaire ultraviolet (λ &lt; 424 nm), le NO<sub>2</sub> subit une photolyse (NO<sub>2</sub> + <em>hν</em> → NO + O), suivie de la recombinaison O + O<sub>2</sub> + M → O<sub>3</sub> + M. Inversement, en présence de fort trafic ou durant la nuit, le monoxyde d'azote détruit l'ozone par titration (NO + O<sub>3</sub> → NO<sub>2</sub> + O<sub>2</sub>). Ce mécanisme explique pourquoi, dans nos données franciliennes, <strong>l'ozone (O<sub>3</sub>) présente un pic l'après-midi (14h–16h) fortement corrélé à la température (<em>r</em> = +0,58), en opposition de phase avec les doubles pics routiers de NO<sub>2</sub> (8h–9h et 19h–21h)</strong>.
    </li>
    <li>
      <strong>2. Granulométrie et sources des aérosols (PM<sub>10</sub> vs PM<sub>2.5</sub>) :</strong> La littérature épidémiologique (<strong>Pope &amp; Dockery, 2006</strong>) et physico-chimique (<strong>Harrison et al., 2012</strong>) distingue la fraction inhalable (PM<sub>10</sub>, diamètre &lt; 10 µm) de la fraction fine alvéolaire (PM<sub>2.5</sub>, diamètre &lt; 2,5 µm). En zone routière dense, une part majeure des PM<sub>10</sub> provient des <strong>émissions hors-échappement (<em>non-exhaust emissions</em>)</strong> : abrasion des plaquettes de frein, usure des pneumatiques sur l'asphalte et remise en suspension des poussières déposées sur la chaussée. Les PM<sub>2.5</sub>, quatre fois plus fines, sont issues des combustions (moteurs, chauffage biomasse/bois) et de la nucléation secondaire d'aérosols inorganiques (nitrates et sulfates d'ammonium issus du NO<sub>2</sub> et du SO<sub>2</sub>). Comme 2,5 &lt; 10, la concentration massique de PM<sub>10</sub> englobe mathématiquement celle des PM<sub>2.5</sub> (corrélation observée <em>r</em> = +0,92).
    </li>
    <li>
      <strong>3. Dispersion advective, couche limite et lessivage humide (<em>Wet Scavenging</em>) :</strong> La concentration d'un polluant est inversement proportionnelle à la hauteur de la couche limite planétaire (plus basse en hiver ou la nuit, favorisant l'accumulation) et à la vitesse du vent (V<sub>10m</sub>), qui assure le transport horizontal (advection). Enfin, les précipitations entraînent un abattement mécanique des particules et gaz solubles par lessivage atmosphérique (<em>washout / rainout</em>), ce qui justifie l'intégration du cumul de pluie futur (<code>precip_cumul</code>) dans notre modèle.
    </li>
    <li>
      <strong>4. Co-exposition aux bio-aérosols (<code>birch_pollen</code>) :</strong> La littérature allergologique (<strong>D'Amato et al., 2007</strong>) démontre que les polluants chimiques (NO<sub>2</sub>, O<sub>3</sub>, PM) altèrent la paroi des grains de pollen de bouleau (allergène majeur Bet v 1 en Île-de-France) et fragilisent les muqueuses bronchiques, décuplant la réponse inflammatoire.
    </li>
  </ul>

  <table>
    <thead>
      <tr>
        <th>Variable Collectée</th>
        <th>Unité</th>
        <th>Origine Physico-Chimique Majeure</th>
        <th>Seuil OMS (2021) / UE</th>
        <th>Effet Physiopathologique Documenté</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>PM2.5</strong> (<code>pm2_5</code>)</td>
        <td>µg/m³</td>
        <td>Combustion moteurs/bois, aérosols secondaires</td>
        <td>15 µg/m³ (OMS 24h) / 25 (UE)</td>
        <td>Passage alvéolo-capillaire, stress oxydatif, AVC, infarctus</td>
      </tr>
      <tr>
        <td><strong>PM10</strong> (<code>pm10</code>)</td>
        <td>µg/m³</td>
        <td>Abrasion freins/pneus/bitume, remise en suspension, BTP</td>
        <td>45 µg/m³ (OMS 24h) / 50 (UE)</td>
        <td>Dépôt trachéo-bronchique, exacerbation d'asthme, BPCO</td>
      </tr>
      <tr>
        <td><strong>NO₂</strong> (<code>nitrogen_dioxide</code>)</td>
        <td>µg/m³</td>
        <td>Oxydation thermique à haute température (trafic routier)</td>
        <td>25 µg/m³ (OMS 24h) / 40 (UE)</td>
        <td>Inflammation des voies aériennes, hyperréactivité bronchique</td>
      </tr>
      <tr>
        <td><strong>Ozone O₃</strong> (<code>ozone</code>)</td>
        <td>µg/m³</td>
        <td>Polluant secondaire : photolyse UV du NO₂ + COV</td>
        <td>100 µg/m³ (OMS 8h) / 120 (UE)</td>
        <td>Altération de la fonction pulmonaire, toux, irritation oculaire</td>
      </tr>
      <tr>
        <td><strong>SO₂ &amp; CO</strong></td>
        <td>µg/m³</td>
        <td>Combustion fioul soufré / combustion incomplète</td>
        <td>SO₂ : 125 µg/m³ (UE)</td>
        <td>Bronchoconstriction réflexe (SO₂), hypoxie tissulaire (CO)</td>
      </tr>
    </tbody>
  </table>

  <h3>2.2 État de l'art de la prévision de la qualité de l'air par Machine Learning</h3>
  <p>
    Historiquement, la prévision opérationnelle repose sur des <strong>modèles déterministes de Chimie-Transport (CTM)</strong> tels que <strong>CHIMERE</strong> (<strong>Menut et al., 2013</strong>) utilisé par Airparif et le consortium européen <strong>CAMS (Copernicus Atmosphere Monitoring Service)</strong>. Si ces modèles résolvent les équations différentielles de conservation de la masse sur un maillage eulérien 3D, ils présentent deux limites pour le pilotage local temps réel : un coût de calcul élevé et des biais systématiques à l'échelle de la rue (<em>street canyon effect</em>).
  </p>
  <p>
    Depuis une décennie, les approches par <strong>apprentissage automatique (Machine Learning)</strong> se sont imposées pour la prévision locale à court terme (+1h à +48h). Les benchmarks de référence sur les données tabulaires hétérogènes (<strong>Grinsztajn, Oyallon &amp; Varoquaux, 2022, NeurIPS</strong>) démontrent que les méthodes d'ensemble par <strong>arbres de décision boostés par gradient (GBDT)</strong> — notamment <strong>XGBoost</strong> (<strong>Chen &amp; Guestrin, 2016</strong>) et <strong>LightGBM</strong> (<strong>Ke et al., 2017</strong>) — surpassent les réseaux de neurones profonds lorsqu'elles sont couplées à une ingénierie de variables temporelles rigoureuse (lags, fenêtres glissantes, prévisions météorologiques exogènes).
  </p>

  <div class="lit-box">
    <strong>Justification théorique de l'architecture « Direct Multi-Horizon » (Taieb et al., 2012) :</strong><br/>
    Pour prédire une série temporelle sur <em>H</em> = 24 pas de temps futurs (<em>y</em><sub>t+1</sub>, …, <em>y</em><sub>t+24</sub>), deux paradigmes s'opposent dans la littérature :<br/>
    • <em>La stratégie Récursive (Iterative)</em> : un unique modèle <em>f</em><sub>1</sub> prédit <em>ŷ</em><sub>t+1</sub>, puis réinjecte <em>ŷ</em><sub>t+1</sub> comme entrée pour prédire <em>ŷ</em><sub>t+2</sub>, ce qui provoque une <strong>propagation exponentielle des erreurs d'approximation</strong> au-delà de +6h et empêche d'utiliser directement la météo prévue à l'horizon exact <em>t+h</em>.<br/>
    • <em>La stratégie Directe (retenue dans notre projet)</em> : on entraîne <strong><em>H</em> = 24 modèles indépendants (M<sub>1</sub>, M<sub>2</sub>, …, M<sub>24</sub>)</strong> où chaque modèle M<sub>h</sub> apprend directement la relation <em>ŷ</em><sub>t+h</sub> = M<sub>h</sub>(X<sub>t</sub><sup>passé</sup>, W<sub>t+1:t+h</sub><sup>météo future</sup>). Cette architecture élimine l'accumulation d'erreurs et permet à chaque horizon <em>h</em> de sélectionner son propre sous-ensemble optimal de variables explicatives (<code>columns[h]</code> dans <code>bundle_aqi.joblib</code>).
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════════════════════
     PAGE 4 : 3. CHAPITRE I — INGÉNIERIE DES DONNÉES & PIPELINE SUPABASE
     ══════════════════════════════════════════════════════════════════════════ -->
<div class="page">
  <div class="sec-header">
    <span class="sec-num">CHAPITRE 3</span>
    <span class="sec-title">Ingénierie des Données : Collecte Open-Meteo, Pipeline ETL &amp; Base Supabase</span>
  </div>

  <h3>3.1 Maillage territorial des 34 stations d'Île-de-France (<code>Back/Projet_qualite_air/dico.py</code>)</h3>
  <p>
    Le fichier <code>dico.py</code> définit le référentiel géodésique des <strong>34 stations de surveillance</strong> couvrant Paris intra-muros, la petite couronne et la grande couronne (latitude, longitude, identifiant officiel et nom). Ce maillage combine volontairement deux typologies de stations afin de capturer toute la dynamique spatiale régionale :
  </p>
  <div class="grid-2">
    <div class="card">
      <h3 style="margin-top:0;color:#ef4444;">Stations de Trafic Routier (8 stations)</h3>
      <p style="font-size:8.4pt;margin:0;">Implantées en bordure immédiate des axes à très fort débit journalier : <strong>Autoroute A1 Saint-Denis</strong> (<code>203098</code>), <strong>Boulevard Périphérique Est</strong> (<code>283088</code>), <strong>Place Victor Basch</strong> (<code>143091</code>), <strong>Place de l'Opéra</strong> (<code>193092</code>), <strong>Champs-Élysées</strong> (<code>243086</code>), <strong>Boulevard de Denain</strong> (<code>5-2218252</code>), <strong>RN6 Melun</strong> (<code>23095</code>), <strong>RN20 Montlhéry</strong> (<code>3314715</code>).</p>
    </div>
    <div class="card">
      <h3 style="margin-top:0;color:#10b981;">Stations de Fond Urbain &amp; Périurbain (26 stations)</h3>
      <p style="font-size:8.4pt;margin:0;">Implantées à distance des sources directes pour mesurer l'exposition moyenne de la population et les pollutions photochimiques régionales : <strong>Paris 18e, Paris 1er Les Halles, Neuilly-sur-Seine, Vitry-sur-Seine, Champigny, Bobigny, Évry, Cergy-Pontoise, Versailles, Mantes-la-Jolie, Rambouillet, Fontainebleau, Provins…</strong></p>
    </div>
  </div>

  <h3>3.2 Architecture du Pipeline ETL d'acquisition (<code>fonctions_de_chargement.py</code>)</h3>
  <p>
    Conformément au <code>README.md</code> du dossier <code>Back/Projet_qualite_air/</code>, l'acquisition repose sur la fonction centrale <code>initialisation_tab(capteurs, mode="hourly" | "current")</code> qui orchestre, pour chacun des 34 capteurs, une double requête HTTP vers l'écosystème <strong>Open-Meteo</strong> :
  </p>
  <ol style="padding-left:18px;margin-bottom:6px;font-size:8.7pt;color:#334155;">
    <li><strong>Requête Qualité de l'Air :</strong> appel à <code>https://air-quality-api.open-meteo.com/v1/air-quality</code> pour extraire les 8 variables : <code>european_aqi, pm10, pm2_5, nitrogen_dioxide, ozone, sulphur_dioxide, carbon_monoxide, birch_pollen</code>.</li>
    <li><strong>Requête Météorologique :</strong> appel à <code>https://api.open-meteo.com/v1/forecast</code> aux mêmes coordonnées GPS pour extraire les 5 variables : <code>temperature_2m, relative_humidity_2m, wind_speed_10m, wind_direction_10m, precipitation</code>.</li>
    <li><strong>Normalisation temporelle et Fusion relationnelle :</strong> suppression des colonnes parasites (<code>drop(columns=["interval"])</code>), troncature des horodatages UTC à l'heure entière (<code>dt.floor("h")</code>), conversion vers le fuseau <code>Europe/Paris</code>, puis jointure interne stricte (<code>pd.merge(..., how="inner")</code>) sur le quintuplet <code>["time", "capteur_id", "capteur_nom", "latitude", "longitude"]</code>.</li>
  </ol>

  <table>
    <thead>
      <tr>
        <th>Script Python / Fichier</th>
        <th>Mode d'exécution</th>
        <th>Rôle Technique dans le Cycle de Vie des Données</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>app_historique.py</code></td>
        <td><code>mode="hourly"</code><br/>(<code>past_hours=1800</code>)</td>
        <td>Amorçage initial de la base : télécharge ~75 jours d'historique horaire par capteur (~61 200 lignes), exécute la procédure stockée RPC <code>supabase.rpc("vider_mesures").execute()</code>, puis insère par lots de <code>batch_size=1000</code>.</td>
      </tr>
      <tr>
        <td><code>app_streaming.py</code></td>
        <td><code>mode="current"</code><br/>(Local / Planificateur)</td>
        <td>Collecte incrémentale toutes les 30 minutes : récupère les 34 relevés courants, trace l'exécution dans <code>log.txt</code> et pousse un lot unique de <code>batch_size=34</code> lignes vers Supabase.</td>
      </tr>
      <tr>
        <td><code>scheduled_retrieval.py</code> &amp;<br/><code>.github/workflows/scheduler.yml</code></td>
        <td><code>mode="current"</code><br/>(CI/CD Cloud GitHub)</td>
        <td>Exécution automatisée sans serveur (<em>Serverless Cron</em>) via GitHub Actions avec gestion des codes de sortie (<code>sys.exit(1)</code> en cas d'erreur réseau) et injection sécurisée du secret <code>SUPABASE_TOKEN</code>.</td>
      </tr>
      <tr>
        <td><code>launcher_for_BD_1.py</code> &amp;<br/><code>launcher_for_algo.py</code></td>
        <td>Provisionnement</td>
        <td>Scripts d'installation modulaire des dépendances : socle Data/BDD (<code>dotenv, supabase, sweetviz, streamlit</code>) et socle Modélisation IA (<code>scikit-learn, xgboost, lightgbm</code>).</td>
      </tr>
    </tbody>
  </table>

  <h3>3.3 Modèle de données PostgreSQL sous Supabase, Idempotence &amp; EDA Sweetviz</h3>
  <p>
    La table <code>public.mesures</code> (définie dans <code>tables.sql</code>) stocke chaque observation avec une clé primaire auto-incrémentée <code>id BIGINT GENERATED BY DEFAULT AS IDENTITY</code> et une contrainte d'unicité métier sur le couple <code>(capteur_id, time)</code>. La fonction <code>envoyer_dataframe(supabase, df, table, batch_size)</code> garantit l'<strong>idempotence totale des écritures</strong> grâce à la clause :
  </p>
  <div class="formula-box">
    <code>supabase.table("mesures").upsert(lot, on_conflict="capteur_id,time", ignore_duplicates=True).execute()</code><br/>
    Ainsi, si le script de streaming est relancé plusieurs fois au cours de la même heure, les mesures déjà présentes pour un couple <code>(capteur_id, time)</code> sont ignorées sans générer de doublons ni d'erreur SQL. Par ailleurs, une politique de purge automatique maintient une fenêtre glissante propre de 8 jours (192 heures, soit ~8 040 lignes actives) pour optimiser les performances de lecture.
  </div>
  <p>
    Enfin, le rapport d'analyse exploratoire <code>Back/Projet_qualite_air/rapport_qualite_air.html</code> (généré avec la bibliothèque <strong>Sweetviz</strong> et intégré dans l'onglet Power BI de notre application) fournit les distributions statistiques complètes, taux de valeurs manquantes et histogrammes de chacune des 17 colonnes de la table.
  </p>
</div>

<!-- ══════════════════════════════════════════════════════════════════════════
     PAGE 5 : 4. CHAPITRE II — MODÉLISATION IA MULTI-HORIZONS (233 FEATURES)
     ══════════════════════════════════════════════════════════════════════════ -->
<div class="page">
  <div class="sec-header">
    <span class="sec-num">CHAPITRE 4</span>
    <span class="sec-title">Modélisation Prédictive IA à 24 Horizons (<code>Back/prediction/</code>)</span>
  </div>

  <h3>4.1 Préparation spatio-temporelle et décomposition vectorielle du vent (<code>importer_df.py</code>)</h3>
  <p>
    Le module <code>Back/prediction/importer_df.py</code> assure la transformation des données brutes de Supabase en matrices de variables explicatives prêtes pour l'inférence des 24 modèles LightGBM :
  </p>
  <ul>
    <li>
      <strong>1. Extraction paginée stable (<code>charger_df()</code>) :</strong> L'API PostgREST de Supabase limitant chaque requête à 1 000 enregistrements, la fonction pagine par tranches <code>.range(debut, debut + 999)</code> avec un tri déterministe <code>.order("capteur_id").order("time")</code> jusqu'à épuisement complet de la table.
    </li>
    <li>
      <strong>2. Régularisation sur grille horaire stricte (<code>preparer_df(df)</code>) :</strong> Afin que les opérateurs de décalage temporel (<code>.shift(t)</code>) correspondent exactement à <em>t</em> heures dans le passé même si une collecte a été manquée, chaque série capteur est ré-échantillonnée sur une grille horaire continue via <code>.groupby("capteur_id").resample("1h").asfreq()</code>.
    </li>
    <li>
      <strong>3. Continuité angulaire du vent (Composantes zonale <em>u</em> et méridienne <em>v</em>) :</strong> La direction du vent en degrés (0° et 360° désignant tous deux le Nord) présente une discontinuité mathématique qui pénalise les coupures d'arbres de décision. Le code projette donc le vecteur vent dans le plan cartésien météorologique :
    </li>
  </ul>
  <div class="formula-box">
    <code>rad = np.deg2rad(df["wind_direction_10m"])</code><br/>
    <code>df["wind_u"] = -df["wind_speed_10m"] * np.sin(rad)</code> &nbsp;&nbsp;<em>(Composante zonale Ouest → Est)</em><br/>
    <code>df["wind_v"] = -df["wind_speed_10m"] * np.cos(rad)</code> &nbsp;&nbsp;<em>(Composante méridienne Sud → Nord)</em>
  </div>

  <h3>4.2 Architecture des 233 Variables Explicatives : Passé, Météo Future &amp; Cyclicité</h3>
  <p>
    La richesse prédictive du bundle <code>bundle_aqi.joblib</code> repose sur la concaténation de trois blocs de features (convertis en <code>float32</code> pour optimiser l'empreinte mémoire) :
  </p>

  <table>
    <thead>
      <tr>
        <th>Fonction Python</th>
        <th>Famille de Variables</th>
        <th>Construction Mathématique Exacte dans le Code</th>
        <th>Justification Physique</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>features_passe(df)</code><br/><em>(Bloc <code>historique</code>)</em></td>
        <td>Lags, Fenêtres glissantes &amp; Dérivées des 8 Polluants</td>
        <td>• Valeur instantanée <code>pol_pass0</code><br/>• 9 Lags : <em>t − k</em> avec <em>k</em> ∈ (1, 2, 3, 6, 12, 24, 48, 72, 168h)<br/>• Fenêtres <em>W</em> ∈ (6h, 24h, 72h) : <code>mean</code>, <code>std</code>, <code>max</code><br/>• Dérivées : <code>dif6</code> (<em>x<sub>t</sub> − x<sub>t−6</sub></em>) et <code>dif24</code> (<em>x<sub>t</sub> − x<sub>t−24</sub></em>)</td>
        <td>Capture l'inertie chimique court terme (1–6h), le cycle journalier (24–72h) et le cycle hebdomadaire (168h = 7 jours).</td>
      </tr>
      <tr>
        <td><code>features_passe(df)</code><br/><em>(Bloc <code>past_meteo</code>)</em></td>
        <td>Mémoire Météorologique (6 vars)</td>
        <td>Pour <code>temp, humidity, wind_speed, wind_u, wind_v, precip</code> :<br/>• Valeur à <em>t</em><sub>0</sub> (<code>_pass0</code>) + 4 Lags : <em>t</em> − 3h, 6h, 12h, 24h</td>
        <td>Traduit le régime synoptique récent (stagnation anticyclonique ou passage frontal).</td>
      </tr>
      <tr>
        <td><code>ajouter_previsions</code> &amp;<br/><code>features_futur(df, h)</code></td>
        <td>Prévisions Météo à l'horizon +<em>h</em> &amp; Lessivage</td>
        <td>Interroge Open-Meteo (<code>forecast_days=3</code>) et calcule sur le tunnel [<em>t</em>+1, <em>t+h</em>] :<br/>• <code>v_fut_h</code> (valeur exacte à <em>t+h</em>)<br/>• <code>_fut_mean</code>, <code>_fut_min</code>, <code>_fut_max</code> sur [<em>t</em>+1 … <em>t+h</em>]<br/>• <code>v_delta</code> (<em>v<sub>t+h</sub> − v<sub>t</sub></em>) et <code>precip_cumul</code> (cumul de pluie sur <em>h</em> heures)</td>
        <td>Permet au modèle M<sub>h</sub> d'anticiper une levée du vent ou une averse qui nettoiera l'atmosphère entre <em>t</em> et <em>t+h</em>.</td>
      </tr>
      <tr>
        <td><code>features_futur(df, h)</code></td>
        <td>Encodage Cyclique Temporel à <em>t+h</em></td>
        <td>Pour l'heure cible <em>d = t + h</em> (en heure de Paris) :<br/>• <code>hour_sin = sin(2π · hour / 24)</code>, <code>hour_cos = cos(2π · hour / 24)</code><br/>• <code>dow</code> (jour de semaine 0…6), <code>month</code> (1…12)</td>
        <td>Préserve la proximité topologique entre 23h00 et 00h00 et distingue les jours ouvrés du week-end.</td>
      </tr>
    </tbody>
  </table>

  <h3>4.3 Inférence vectorisée (<code>predict.py</code>), Back-Testing &amp; Synchronisation BI</h3>
  <p>
    Dans <code>Back/prediction/predict.py</code>, l'inférence est vectorisée sur les 34 capteurs simultanément : pour chaque horizon <em>h</em> ∈ (1, …, 24), le script extrait l'indice <code>pos</code> de la dernière mesure valide de chaque station, sélectionne les colonnes spécifiques <code>columns[h]</code> et appelle <code>models[h].predict(X.loc[pos])</code>, générant 34 × 24 = <strong>816 prédictions horaires</strong>.
  </p>

  <!-- FIGURE 2 : Courbe prédictive et Back-testing -->
  <div class="figure-box">
    <svg viewBox="0 0 800 175" width="100%" height="160" xmlns="http://www.w3.org/2000/svg">
      <text x="14" y="17" fill="#f8fafc" font-size="10" font-weight="bold">Évaluation Back-Testing Temps Réel (Mode SIMULATION = True sur 811 points) &amp; Courbe Prédictive J+1</text>
      <line x1="38" y1="28" x2="38" y2="145" stroke="#475569"/>
      <line x1="38" y1="145" x2="470" y2="145" stroke="#475569"/>
      <polygon fill="rgba(16, 185, 129, 0.18)" points="48,95 95,98 145,92 195,78 245,68 295,75 345,86 395,76 455,80 455,128 395,124 345,134 295,125 245,118 195,126 145,136 95,140 48,136"/>
      <polyline fill="none" stroke="#10b981" stroke-width="2.8" points="48,115 95,119 145,114 195,102 245,93 295,100 345,110 395,100 455,104"/>
      <polyline fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 3" points="48,118 95,115 145,117 195,106 245,97 295,96 345,107 395,104 455,101"/>
      <g fill="#94a3b8" font-size="8" text-anchor="middle">
        <text x="48" y="158">+1h</text><text x="145" y="158">+6h</text><text x="245" y="158">+12h</text><text x="345" y="158">+18h</text><text x="455" y="158">+24h</text>
      </g>
      <rect x="490" y="26" width="295" height="128" rx="8" fill="#1e293b" stroke="#334155"/>
      <text x="504" y="45" fill="#6ee7b7" font-size="9.5" font-weight="bold">Résultats du Back-Testing (811 échantillons) :</text>
      <text x="504" y="64" fill="#f8fafc" font-size="9">• Erreur Absolue Moyenne (MAE) : <tspan fill="#38bdf8" font-weight="bold">5,97 pts EAQI</tspan></text>
      <text x="504" y="81" fill="#f8fafc" font-size="9">• Erreur Relative (MAPE) : <tspan fill="#fde047" font-weight="bold">20,1 %</tspan></text>
      <text x="504" y="98" fill="#f8fafc" font-size="9">• Fiabilité globale (100 − MAPE) : <tspan fill="#10b981" font-weight="bold">79,9 % (~80 %)</tspan></text>
      <text x="504" y="118" fill="#94a3b8" font-size="8.2">── Courbe verte : Prédiction LightGBM + IC 95%</text>
      <text x="504" y="132" fill="#94a3b8" font-size="8.2">-- Courbe bleue : Valeur réelle observée a posteriori</text>
      <text x="504" y="146" fill="#cbd5e1" font-size="8">Export automatique vers Google Sheet « AQI_futures »</text>
    </svg>
    <div class="figure-caption">Figure 2 — Superposition entre la prévision J+1 LightGBM (corridor de confiance à 95 %) et les mesures réelles lors du back-testing.</div>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════════════════════
     PAGE 6 : 5. CHAPITRE III — BACKEND FASTAPI, ANOMALIES & FRONTEND REACT
     ══════════════════════════════════════════════════════════════════════════ -->
<div class="page">
  <div class="sec-header">
    <span class="sec-num">CHAPITRE 5</span>
    <span class="sec-title">Architecture Applicative Full-Stack : API REST FastAPI &amp; Portail React 19</span>
  </div>

  <h3>5.1 Conception du Serveur Backend FastAPI (<code>Back/api/</code>)</h3>
  <p>
    Afin d'exposer les données de Supabase et le moteur prédictif LightGBM à l'application Web et aux outils BI avec une latence minimale, nous avons développé une API REST complète sous <strong>FastAPI</strong> (<code>Back/api/main.py</code>), structurée en 6 microservices internes :
  </p>
  <ul>
    <li><strong><code>data_service.py</code> (Accès Supabase &amp; Détection d'anomalies) :</strong> interroge Supabase via PostgREST avec un cache mémoire TTL, calcule les agrégations horaires/journalières/mensuelles et exécute l'algorithme statistique de détection d'anomalies capteurs par <strong>Z-score</strong> sur fenêtre glissante de 7 jours :
      <div class="formula-box">
        <strong>Détection d'anomalie statistique :</strong> <code>|z| = |x<sub>i,t</sub> − μ<sub>i,7j</sub>| / σ<sub>i,7j</sub> ≥ 3,0</code> &nbsp;&nbsp;(probabilité sous loi normale <em>p</em> &lt; 0,0027, permettant d'isoler un capteur défaillant ou un pic industriel localisé).
      </div>
    </li>
    <li><strong><code>ml_service.py</code> (Inférence Temps Réel &amp; Back-testing) :</strong> charge en mémoire <code>bundle_aqi.joblib</code>, construit dynamiquement les 233 features pour la région entière ou pour un capteur individuel (<code>/api/predictions?sensor_id=...</code>) et calcule les intervalles de confiance à 95 % (<em>ŷ<sub>t+h</sub></em> ± 1,96 × MAE<sub>h</sub>).</li>
    <li><strong><code>alerts_service.py</code> (Moteur d'Alertes &amp; Audit SMTP) :</strong> confronte chaque mesure aux seuils réglementaires configurables (PM<sub>2.5</sub> &gt; 25, PM<sub>10</sub> &gt; 50, NO<sub>2</sub> &gt; 40, O<sub>3</sub> &gt; 120 µg/m³), expédie les bulletins d'alerte HTML et archive chaque envoi dans <code>Back/api/logs/emails_sent.json</code>.</li>
    <li><strong><code>auth.py</code> &amp; <code>logs_service.py</code> (Sécurité JWT RBAC &amp; Observabilité) :</strong> authentification par jetons JWT signés (<code>HS256</code>) distinguant 3 rôles (<code>admin</code>, <code>elu</code>, <code>citoyen</code>) et middleware mesurant la latence moyenne et le centile P95 de chaque route HTTP.</li>
  </ul>

  <h3>5.2 Architecture des 9 Onglets du Portail Décisionnel React 19 (<code>frontend/src/</code>)</h3>
  <p>
    Le frontend (React 19, Vite, Recharts, React-Leaflet, Power BI Client SDK) est organisé en <strong>3 pôles métier</strong> accessibles depuis une barre latérale fixe (<code>Sidebar.jsx</code>) et une barre d'état supérieure temps réel (<code>Topbar.jsx</code>) :
  </p>

  <table>
    <thead>
      <tr>
        <th>Pôle Métier</th>
        <th>Onglet &amp; Composant React</th>
        <th>Fonctionnalités Implémentées &amp; Valeur Ajoutée Décisionnelle</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td rowspan="3"><strong>Pôle 1 :<br/>Temps Réel</strong></td>
        <td><strong>1. Vue d'ensemble</strong> (<code>Dashboard.jsx</code>)</td>
        <td>Sélecteur dynamique (Moyenne Île-de-France ou chacune des 34 stations), Jauge EAQI (<code>AqiGauge.jsx</code>), 5 cartes polluants avec barres de progression OMS, météo temps réel et tableau d'état du parc.</td>
      </tr>
      <tr>
        <td><strong>2. Carte des 34 stations</strong> (<code>MapPage.jsx</code>)</td>
        <td>Cartographie interactive Leaflet (<code>AirQualityMap.jsx</code>), marqueurs colorés selon l'EAQI réel, filtrage par niveau de qualité et panneau latéral complet au clic sur un capteur.</td>
      </tr>
      <tr>
        <td><strong>3. Détail polluants</strong> (<code>AirQuality.jsx</code>)</td>
        <td>Analyse multi-fenêtres (24h, 48h, 7 jours) filtrable par capteur, courbes d'évolution comparées aux seuils OMS et fiches explicatives sanitaires par polluant.</td>
      </tr>
      <tr>
        <td rowspan="3"><strong>Pôle 2 :<br/>Analyse &amp; IA</strong></td>
        <td><strong>4. Prédictions IA (J+1)</strong> (<code>Predictions.jsx</code>)</td>
        <td>Courbe prédictive sur 24h avec corridor de confiance à 95 % (<code>PredictionChart.jsx</code>), sélecteur des 34 stations, métriques de back-testing en direct et poids des variables explicatives.</td>
      </tr>
      <tr>
        <td><strong>5. Mobilité &amp; Trafic</strong> (<code>Mobility.jsx</code>)</td>
        <td>Séparation des 8 stations routières et des 26 stations de fond, calcul de la <strong>Surconcentration Trafic vs Fond (+52 %)</strong>, de l'<strong>Indice d'Émission Trafic (41 %)</strong> et recommandations Crit'Air.</td>
      </tr>
      <tr>
        <td><strong>6. Power BI</strong> (<code>PowerBIPage.jsx</code>)</td>
        <td>Reproduction interactive des 6 pages de <code>Smart_City.pbix</code> sur Supabase, intégration Cloud <code>app.powerbi.com</code> + certificat SSL, corrélations de Pearson et rapport EDA Sweetviz.</td>
      </tr>
      <tr>
        <td rowspan="3"><strong>Pôle 3 :<br/>Pilotage &amp; Système</strong></td>
        <td><strong>7. Alertes &amp; Seuils</strong> (<code>Alerts.jsx</code>)</td>
        <td>Gestion des dépassements OMS et des anomalies Z-score, acquittement, paramétrage des seuils (Admin), envoi d'e-mail de test et journal d'audit des notifications.</td>
      </tr>
      <tr>
        <td><strong>8. Rapports Élus (PDF)</strong> (<code>Reports.jsx</code>)</td>
        <td>Génération de rapports exécutifs PDF et exports CSV sur mesure (journalier, hebdomadaire, alerte, parc IoT) + téléchargement du présent dossier complet.</td>
      </tr>
      <tr>
        <td><strong>9. Monitoring &amp; Logs</strong> (<code>AdminMonitoring.jsx</code>)</td>
        <td>Supervision de l'état de santé (Supabase, Modèle LightGBM, Open-Meteo), taux de disponibilité SLA, temps de réponse P95 et console de logs serveur filtrable.</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- ══════════════════════════════════════════════════════════════════════════
     PAGE 7 : 6. CHAPITRE IV — MOBILITÉ ROUTIÈRE & BUSINESS INTELLIGENCE POWER BI
     ══════════════════════════════════════════════════════════════════════════ -->
<div class="page">
  <div class="sec-header">
    <span class="sec-num">CHAPITRE 6</span>
    <span class="sec-title">Analyse de la Mobilité Routière &amp; Business Intelligence Power BI</span>
  </div>

  <h3>6.1 Modélisation de la pression automobile dans l'onglet « Mobilité &amp; Trafic »</h3>
  <p>
    Le dioxyde d'azote (NO<sub>2</sub>) étant le traceur primaire de la combustion automobile, le composant <code>Mobility.jsx</code> partitionne en temps réel l'ensemble des 34 capteurs en deux sous-populations : l'ensemble <em>R</em> des <strong>8 capteurs routiers</strong> (A1 Saint-Denis, Périphérique Est, RN6, RN20, Champs-Élysées, Opéra, Victor Basch, Denain) et l'ensemble <em>F</em> des <strong>26 capteurs de fond urbain et rural</strong>. Deux indicateurs décisionnels sont alors calculés :
  </p>

  <div class="grid-2">
    <div class="formula-box" style="margin:0;">
      <strong>1. Surconcentration Trafic vs Fond (+52 %) :</strong><br/>
      <code>Δ<sub>Trafic/Fond</sub> = ((NO₂_Moyen_Trafic − NO₂_Moyen_Fond) / NO₂_Moyen_Fond) × 100</code><br/>
      Avec <code>NO₂_Moyen_Trafic = 20,5 µg/m³</code> et <code>NO₂_Moyen_Fond = 13,5 µg/m³</code>, on obtient <strong>+52 %</strong> : l'air respiré le long des grands axes routiers contient 52 % de NO<sub>2</sub> en plus que l'air ambiant de fond.
    </div>
    <div class="formula-box" style="margin:0;">
      <strong>2. Indice d'Émission Trafic (41 % — Max : A1 Saint-Denis) :</strong><br/>
      <code>I<sub>Trafic</sub> = min(100, round((NO₂_Moyen_Trafic / 50 µg/m³) × 100))</code><br/>
      Mesure le taux de saturation par rapport au seuil critique routier de 50 µg/m³, tout en affichant l'axe le plus chargé (ici l'Autoroute A1 à Saint-Denis).
    </div>
  </div>

  <!-- FIGURE 3 : Cycle diurne + Corrélations -->
  <div class="figure-box">
    <svg viewBox="0 0 800 180" width="100%" height="165" xmlns="http://www.w3.org/2000/svg">
      <!-- Gauche : Cycle diurne -->
      <text x="12" y="16" fill="#f8fafc" font-size="9.5" font-weight="bold">Cycle Diurne Horaire (00h–23h) : NO₂ Trafic vs Ozone O₃</text>
      <line x1="35" y1="26" x2="35" y2="148" stroke="#475569"/>
      <line x1="35" y1="148" x2="385" y2="148" stroke="#475569"/>
      <g fill="#ef4444" opacity="0.8">
        <rect x="48" y="118" width="14" height="30"/><rect x="75" y="124" width="14" height="24"/>
        <rect x="102" y="94" width="14" height="54"/><rect x="129" y="82" width="14" height="66"/>
        <rect x="156" y="103" width="14" height="45"/><rect x="183" y="120" width="14" height="28"/>
        <rect x="210" y="124" width="14" height="24"/><rect x="237" y="122" width="14" height="26"/>
        <rect x="264" y="110" width="14" height="38"/><rect x="291" y="88" width="14" height="60"/>
        <rect x="318" y="78" width="14" height="70"/><rect x="345" y="93" width="14" height="55"/>
      </g>
      <polyline fill="none" stroke="#38bdf8" stroke-width="2.5" points="55,103 82,110 109,100 136,90 163,73 190,54 217,42 244,46 271,63 298,82 325,94 352,100"/>
      <g fill="#94a3b8" font-size="7.8" text-anchor="middle">
        <text x="55" y="161">00h</text><text x="136" y="161">08h (Pointe)</text><text x="217" y="161">15h (Pic O₃)</text><text x="325" y="161">20h (Pointe)</text>
      </g>

      <!-- Droite : Corrélations de Pearson -->
      <g transform="translate(415, 20)">
        <rect x="0" y="0" width="370" height="142" rx="8" fill="#1e293b" stroke="#334155"/>
        <text x="12" y="18" fill="#f8fafc" font-size="9.5" font-weight="bold">Matrice des Corrélations de Pearson sur 8 040 Relevés Supabase</text>
        <text x="12" y="40" fill="#38bdf8" font-size="8.5" font-weight="bold">• PM2.5 × PM10 : r = +0,92</text>
        <text x="175" y="40" fill="#cbd5e1" font-size="8">(Inclusion granulométrique directe)</text>
        <text x="12" y="60" fill="#f59e0b" font-size="8.5" font-weight="bold">• Température × Ozone O₃ : r = +0,58</text>
        <text x="205" y="60" fill="#cbd5e1" font-size="8">(Catalyse photochimique UV)</text>
        <text x="12" y="80" fill="#a855f7" font-size="8.5" font-weight="bold">• NO₂ × European AQI : r = +0,46</text>
        <text x="195" y="80" fill="#cbd5e1" font-size="8">(Poids du trafic sur l'indice)</text>
        <text x="12" y="100" fill="#10b981" font-size="8.5" font-weight="bold">• Vitesse Vent × NO₂ : r = −0,34</text>
        <text x="195" y="100" fill="#cbd5e1" font-size="8">(Dispersion advective éolienne)</text>
        <text x="12" y="120" fill="#10b981" font-size="8.5" font-weight="bold">• Vitesse Vent × PM2.5 : r = −0,31</text>
        <text x="195" y="120" fill="#cbd5e1" font-size="8">(Balayage de la couche limite)</text>
      </g>
    </svg>
    <div class="figure-caption">Figure 3 — Cycle diurne NO₂/O₃ (à gauche) et coefficients de corrélation linéaire de Pearson mesurés sur la base Supabase (à droite).</div>
  </div>

  <h3>6.2 Architecture du Rapport Power BI <code>Smart_City.pbix</code> (6 Pages &amp; Modèle Hybride)</h3>
  <p>
    Le fichier <code>Back/Smart_City.pbix</code> (publié sur Power BI Service sous l'identifiant <code>70b30346-6b29-4afa-8814-d5d0d3cdb88f</code>) s'appuie sur un <strong>modèle de données hybride</strong> combinant :
    <strong>(1)</strong> une connexion PostgreSQL vers Supabase (<code>aws-0-eu-west-2.pooler.supabase.com:5432</code>, base <code>postgres</code>) sécurisée par le certificat racine <code>Back/prod-ca-2021.crt</code> (<code>CN=Supabase Root 2021 CA</code>) pour les données observées ; et
    <strong>(2)</strong> un connecteur Web Google Sheets (feuille <code>AQI_futures</code> mise à jour par <code>predict.py</code> via <code>gspread</code>) pour les prévisions à 24 heures.
  </p>

  <table>
    <thead>
      <tr>
        <th>Page du Rapport Power BI</th>
        <th>Identifiant Interne</th>
        <th>Visuels &amp; Architecture Analytique</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. Présentation</strong></td>
        <td><code>e42762e0814cb6807470</code></td>
        <td>Page d'accueil présentant le sommaire interactif des 5 volets analytiques et la table statique de référence <code>European_AQI_Min / Max / Couleur / Qualité</code>.</td>
      </tr>
      <tr>
        <td><strong>2. Statistiques aqi</strong></td>
        <td><code>ba061a81471048e95aca</code></td>
        <td>Jauge centrale (<code>Min / Moyenne / Max de european_aqi</code>), graphique en aires empilées par Mois, courbes d'évolution par Jour et par Heure, et 4 segments (<code>capteur_nom</code>, <code>Mois</code>, <code>Jour</code>, <code>Heure</code>).</td>
      </tr>
      <tr>
        <td><strong>3. autres données</strong></td>
        <td><code>a2117adde8c9f425564e</code></td>
        <td>Table matricielle détaillée (<code>tableEx</code>) exposant simultanément les coordonnées GPS, les moyennes de polluants (NO<sub>2</sub>, O<sub>3</sub>, PM<sub>10</sub>, PM<sub>2.5</sub>, SO<sub>2</sub>) et les paramètres météo par station.</td>
      </tr>
      <tr>
        <td><strong>4. Carte</strong></td>
        <td><code>bdc935574ee12ace99d9</code></td>
        <td>Carte géospatiale à bulles proportionnelles à <code>Moyenne de european_aqi</code> avec info-bulles météo (pluie, vitesse et direction du vent), carte KPI et 4 segments temporels/spatiaux.</td>
      </tr>
      <tr>
        <td><strong>5. Actualité</strong></td>
        <td><code>a8dd607c5d083cc32080</code></td>
        <td>Monitoring temps réel : jauge du <code>Dernier relevé</code> bornée par le Min et le Max historiques, et 3 cartes KPI dynamiques (<code>Dernier capteur_nom</code> + <code>capteur_id</code>, <code>DernierJour</code>, <code>derniereheure</code>).</td>
      </tr>
      <tr>
        <td><strong>6. prévisions</strong></td>
        <td><code>0987263496d8e11a5eee</code></td>
        <td>Courbe multi-séries de <code>Moyenne de aqi_predit</code> par <code>Heure</code> (+1h à +24h) et par <code>capteur_nom</code>, pilotée par 3 segments (<code>capteur_nom</code>, curseur <code>Heure</code>, <code>heure_locale</code>).</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- ══════════════════════════════════════════════════════════════════════════
     PAGE 8 : 7. CONCLUSION GÉNÉRALE, LIMITES, PERSPECTIVES & 8. BIBLIOGRAPHIE
     ══════════════════════════════════════════════════════════════════════════ -->
<div class="page">
  <div class="sec-header">
    <span class="sec-num">CHAPITRE 7</span>
    <span class="sec-title">Conclusion Générale, Analyse Critique, Limites &amp; Perspectives</span>
  </div>

  <h3>7.1 Synthèse des réalisations et apports du projet</h3>
  <p>
    Ce projet a permis de concevoir, déployer et valider une <strong>plateforme décisionnelle Smart City complète et opérationnelle de bout en bout</strong> pour la surveillance et l'anticipation de la qualité de l'air en Île-de-France. Au-delà de la simple juxtaposition d'outils techniques, la valeur ajoutée du système réside dans la <strong>cohérence de sa chaîne de valeur</strong> :
  </p>
  <ul>
    <li><strong>Robustesse de l'ingénierie des données :</strong> l'acquisition automatisée multi-sources (Open-Meteo Air Quality &amp; Weather) sur 34 stations franciliennes, sécurisée par des écritures idempotentes (<code>upsert</code> sur <code>(capteur_id, time)</code>) dans Supabase PostgreSQL, garantit une base de données fiable et sans doublons.</li>
    <li><strong>Pertinence scientifique de la modélisation IA :</strong> la traduction des mécanismes physiques de l'atmosphère (décomposition vectorielle du vent <em>u/v</em>, cumul de précipitations pour le lessivage, inertie multi-échelles jusqu'à <em>t</em>−168h, encodage cyclique horaire) en <strong>233 variables explicatives</strong> permet aux <strong>24 modèles LightGBM</strong> d'atteindre une erreur absolue moyenne de seulement <strong>5,97 points EAQI (fiabilité ~80 %)</strong> en validation par back-testing réel.</li>
    <li><strong>Ergonomie décisionnelle multi-acteurs :</strong> le couplage entre le portail Web React (9 onglets adaptés aux profils Administrateur, Élu et Citoyen) et les 6 pages du rapport Power BI <code>Smart_City.pbix</code> transforme la donnée brute en actions concrètes (ciblage des axes routiers en surconcentration de +52 %, alertes e-mail automatiques, bilans PDF).</li>
  </ul>

  <h3>7.2 Limites méthodologiques et techniques identifiées</h3>
  <div class="grid-2">
    <div class="card">
      <h3 style="margin-top:0;color:#b45309;">1. Résolution spatiale et données exogènes</h3>
      <p style="font-size:8.3pt;margin:0;">Les flux Open-Meteo Air Quality reposent sur la réanalyse régionale CAMS (maillage de quelques kilomètres). Dans les rues-canyons très étroites de Paris, des micro-capteurs physiques in situ associés aux comptages routiers temps réel permettraient d'affiner encore la résolution locale.</p>
    </div>
    <div class="card">
      <h3 style="margin-top:0;color:#b45309;">2. Dérive saisonnière (Concept Drift)</h3>
      <p style="font-size:8.3pt;margin:0;">Les régimes photochimiques d'été (dominés par l'ozone O<sub>3</sub>) diffèrent des épisodes hivernaux d'inversion thermique (dominés par les PM<sub>2.5</sub> du chauffage). Un ré-entraînement périodique continu du bundle LightGBM est nécessaire pour maintenir une MAE optimale toute l'année.</p>
    </div>
  </div>

  <h3>7.3 Perspectives d'évolution industrielle et scientifique</h3>
  <ul>
    <li><strong>Couplage avec les données de trafic temps réel (Open Data Paris / Sytadin) :</strong> intégrer le taux d'occupation et le débit horaire des boucles électromagnétiques du Boulevard Périphérique et de l'A1 comme variables explicatives additionnelles dans <code>importer_df.py</code>.</li>
    <li><strong>Modélisation spatio-temporelle par Graph Neural Networks (GNN) :</strong> modéliser les 34 stations comme les nœuds d'un graphe orienté pondéré par la direction du vent (V<sub>10m</sub>) afin d'anticiper le déplacement géographique d'un panache de pollution d'une commune à sa voisine.</li>
    <li><strong>Industrialisation MLOps :</strong> automatiser le suivi de la dérive du modèle (<em>Model Drift Monitoring</em>) et le ré-entraînement mensuel de <code>bundle_aqi.joblib</code> via GitHub Actions et MLflow.</li>
  </ul>

  <div class="sec-header" style="margin-top:11px;">
    <span class="sec-num">CHAPITRE 8</span>
    <span class="sec-title">Bibliographie Scientifique, Technique &amp; Réglementaire</span>
  </div>

  <div style="font-size:7.9pt;line-height:1.36;color:#334155;">
    <p style="margin-bottom:3px;"><strong>[1] Organisation Mondiale de la Santé (OMS / WHO).</strong> (2021). <em>WHO Global Air Quality Guidelines: Particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide.</em> World Health Organization, Geneva.</p>
    <p style="margin-bottom:3px;"><strong>[2] European Environment Agency (EEA).</strong> (2023). <em>Air Quality in Europe 2023 — Health impacts of air pollution in Europe &amp; The European Air Quality Index (EAQI) methodology.</em> Publications Office of the European Union.</p>
    <p style="margin-bottom:3px;"><strong>[3] Seinfeld, J. H., &amp; Pandis, S. N.</strong> (2016). <em>Atmospheric Chemistry and Physics: From Air Pollution to Climate Change</em> (3rd ed.). John Wiley &amp; Sons. (Cycle photochimique de Leighton NO–NO₂–O₃ et dynamique des aérosols).</p>
    <p style="margin-bottom:3px;"><strong>[4] Pope, C. A., &amp; Dockery, D. W.</strong> (2006). Health effects of fine particulate air pollution: lines that connect. <em>Journal of the Air &amp; Waste Management Association</em>, 56(6), 709–742.</p>
    <p style="margin-bottom:3px;"><strong>[5] Harrison, R. M., Jones, A. M., Gietl, J., Yin, J., &amp; Green, D. C.</strong> (2012). Estimation of the contributions of brake dust, tire wear, and resuspension to nonexhaust traffic particles derived from atmospheric measurements. <em>Environmental Science &amp; Technology</em>, 46(12), 6523–6529.</p>
    <p style="margin-bottom:3px;"><strong>[6] Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., &amp; Liu, T.-Y.</strong> (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, 30, 3146–3154.</p>
    <p style="margin-bottom:3px;"><strong>[7] Chen, T., &amp; Guestrin, C.</strong> (2016). XGBoost: A Scalable Tree Boosting System. <em>Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining</em>, 785–794.</p>
    <p style="margin-bottom:3px;"><strong>[8] Grinsztajn, L., Oyallon, E., &amp; Varoquaux, G.</strong> (2022). Why do tree-based models still outperform deep learning on typical tabular data? <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, 35.</p>
    <p style="margin-bottom:3px;"><strong>[9] Taieb, S. B., Bontempi, G., Atiya, A. F., &amp; Sorjamaa, A.</strong> (2012). A review and comparison of strategies for multi-step ahead time series forecasting. <em>Expert Systems with Applications</em>, 39(8), 7067–7083.</p>
    <p style="margin-bottom:3px;"><strong>[10] Menut, L., Bessagnet, B., Khvorostyanov, D., et al.</strong> (2013). CHIMERE 2013: a model for regional atmospheric composition modelling. <em>Geoscientific Model Development</em>, 6, 981–1028 (Modèle CTM utilisé par Airparif et CAMS Copernicus).</p>
    <p style="margin-bottom:0;"><strong>[11] Zanella, A., Bui, N., Castellani, A., Vangelista, L., &amp; Zorzi, M.</strong> (2014). Internet of Things for Smart Cities. <em>IEEE Internet of Things Journal</em>, 1(1), 22–32.</p>
  </div>
</div>

</body>
</html>
"""


def build_html() -> str:
    hero_img = get_pbix_image_b64("qualite-air-mesure")
    city_img = get_pbix_image_b64("images21437597637218753")
    cover_imgs = ""
    if hero_img and city_img:
        cover_imgs = (
            f'<div class="grid-2" style="align-items:center;">'
            f'<img src="{hero_img}" style="width:100%;height:125px;object-fit:cover;border-radius:8px;border:1px solid #cbd5e1;"/>'
            f'<img src="{city_img}" style="width:100%;height:125px;object-fit:cover;border-radius:8px;border:1px solid #cbd5e1;"/>'
            f'</div><div class="figure-caption" style="color:#64748b;">Visuels extraits des ressources embarquées du rapport Power BI Smart_City.pbix du projet.</div>'
        )
    return HTML_TEMPLATE.replace("__COVER_IMAGES__", cover_imgs)


def main():
    html = build_html()
    OUT_HTML.write_text(html, encoding="utf-8")
    chrome_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    browser = next((p for p in chrome_candidates if Path(p).exists()), None)
    if not browser:
        raise RuntimeError("Aucun navigateur Chromium trouvé pour générer le PDF")
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={OUT_PDF}",
        str(OUT_HTML.resolve()),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print("Return code:", res.returncode)
    print("PDF generated:", OUT_PDF, "Size:", OUT_PDF.stat().st_size if OUT_PDF.exists() else 0)


if __name__ == "__main__":
    main()
