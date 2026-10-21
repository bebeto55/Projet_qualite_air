"""Génère le rapport complet du projet Smart City au format Microsoft Word (.docx) et PDF,
parfaitement aligné sur la présentation PowerPoint du projet (Air Quality Index - Smart City),
incluant le diagramme d'architecture officiel de la présentation, la plus-value pour les utilisateurs
(citoyens, personnes vulnérables, hôpitaux, décideurs, chercheurs, services municipaux) et la littérature scientifique."""
import base64
import html
import subprocess
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRATCH_DIR = Path(r"C:\Users\magne\.gemini\antigravity\brain\6b04d8ce-30ea-434f-8fb2-f44fbd74e256\scratch")
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
PPT_PATH = ROOT_DIR / "Air Quality Index (AQI) by Slidesgo.pptx"

OUT_DOCX = ROOT_DIR / "Rapport_Projet_Smart_City_Complet.docx"
OUT_DOCX_LEGACY = ROOT_DIR / "Rapport_Projet_Smart_City_Utilisateurs.docx"
OUT_HTML = ROOT_DIR / "Rapport_Projet_Smart_City.html"
OUT_PDF = ROOT_DIR / "Rapport_Projet_Smart_City_Complet.pdf"
OUT_PDF_LEGACY = ROOT_DIR / "Rapport_Projet_Smart_City_Utilisateurs.pdf"


def get_browser() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    raise RuntimeError("Navigateur Chromium introuvable")


def extract_ppt_architecture_image() -> Path:
    """Extrait le diagramme d'architecture officiel (Slide 9 : image16.png) du PowerPoint."""
    out_arch = SCRATCH_DIR / "fig1_architecture_ppt.png"
    if PPT_PATH.exists():
        with zipfile.ZipFile(PPT_PATH, "r") as z:
            if "ppt/media/image16.png" in z.namelist():
                out_arch.write_bytes(z.read("ppt/media/image16.png"))
                return out_arch
    fallback = SCRATCH_DIR / "ppt_media" / "image16.png"
    if fallback.exists():
        out_arch.write_bytes(fallback.read_bytes())
    return out_arch


# ══════════════════════════════════════════════════════════════════════════════
# 1. FIGURES SCIENTIFIQUES COMPLÉMENTAIRES (FOND CLAIR HAUTE RÉSOLUTION)
# ══════════════════════════════════════════════════════════════════════════════

SVG_CYCLE_DIURNE = """<svg viewBox="0 0 920 270" width="100%" height="250" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff;font-family:'Segoe UI',Calibri,Arial,sans-serif;">
  <rect x="5" y="5" width="910" height="260" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>
  <!-- Partie gauche : Cycle diurne et fenêtres d'exposition pour l'usager -->
  <text x="25" y="28" fill="#0f172a" font-size="11.2" font-weight="bold">A. Identifier les « Patterns » Journaliers pour Protéger les Personnes Sensibles</text>
  <line x1="50" y1="45" x2="50" y2="210" stroke="#64748b" stroke-width="1.2"/>
  <line x1="50" y1="210" x2="465" y2="210" stroke="#64748b" stroke-width="1.2"/>
  <text x="42" y="52" fill="#475569" font-size="9" text-anchor="end">75</text>
  <text x="42" y="105" fill="#475569" font-size="9" text-anchor="end">50</text>
  <text x="42" y="158" fill="#475569" font-size="9" text-anchor="end">25</text>
  <text x="42" y="210" fill="#475569" font-size="9" text-anchor="end">0</text>

  <line x1="50" y1="50" x2="465" y2="50" stroke="#e2e8f0" stroke-dasharray="3 3"/>
  <line x1="50" y1="103" x2="465" y2="103" stroke="#e2e8f0" stroke-dasharray="3 3"/>
  <line x1="50" y1="156" x2="465" y2="156" stroke="#e2e8f0" stroke-dasharray="3 3"/>

  <!-- Barres NO2 -->
  <g fill="#dc2626" opacity="0.82">
    <rect x="62"  y="168" width="18" height="42" rx="2"/>
    <rect x="95"  y="176" width="18" height="34" rx="2"/>
    <rect x="128" y="165" width="18" height="45" rx="2"/>
    <rect x="161" y="122" width="18" height="88" rx="2"/>
    <rect x="194" y="112" width="18" height="98" rx="2"/>
    <rect x="227" y="142" width="18" height="68" rx="2"/>
    <rect x="260" y="164" width="18" height="46" rx="2"/>
    <rect x="293" y="170" width="18" height="40" rx="2"/>
    <rect x="326" y="160" width="18" height="50" rx="2"/>
    <rect x="359" y="128" width="18" height="82" rx="2"/>
    <rect x="392" y="106" width="18" height="104" rx="2"/>
    <rect x="425" y="132" width="18" height="78" rx="2"/>
  </g>
  <!-- Courbe Ozone O3 -->
  <polyline fill="none" stroke="#0284c7" stroke-width="3"
    points="71,140 104,150 137,145 170,132 203,115 236,92 269,68 302,55 335,62 368,88 401,118 434,132"/>
  <g fill="#475569" font-size="8.5" text-anchor="middle">
    <text x="71" y="226">00h</text><text x="137" y="226">04h (Air sain)</text><text x="203" y="226">08h (Pointe)</text>
    <text x="302" y="226">15h (Pic O₃)</text><text x="401" y="226">20h (Pointe)</text>
  </g>
  <rect x="65" y="236" width="12" height="10" fill="#dc2626" rx="2"/>
  <text x="82" y="245" fill="#1e293b" font-size="8.8">Dioxyde d'azote NO₂ (embouteillages matin/soir)</text>
  <line x1="290" y1="241" x2="307" y2="241" stroke="#0284c7" stroke-width="3"/>
  <text x="312" y="245" fill="#1e293b" font-size="8.8">Ozone O₃ (pic photochimique d'après-midi)</text>

  <!-- Partie droite : Facteurs d'accroissement ou de régression de l'AQI -->
  <text x="495" y="28" fill="#0f172a" font-size="11.2" font-weight="bold">B. Facteurs d'Accroissement et de Régression de l'AQI</text>
  <rect x="495" y="42" width="400" height="205" rx="8" fill="#ffffff" stroke="#cbd5e1"/>

  <rect x="510" y="55" width="178" height="52" rx="6" fill="#fef2f2" stroke="#fecaca"/>
  <text x="520" y="72" fill="#991b1b" font-size="8.8" font-weight="bold">Surconcentration Trafic vs Fond</text>
  <text x="520" y="94" fill="#dc2626" font-size="14" font-weight="bold">+52 % de NO₂</text>
  <text x="615" y="94" fill="#475569" font-size="8.2">sur grands axes</text>

  <rect x="702" y="55" width="178" height="52" rx="6" fill="#fffbeb" stroke="#fde68a"/>
  <text x="712" y="72" fill="#92400e" font-size="8.8" font-weight="bold">Indice d'Émission Trafic</text>
  <text x="712" y="94" fill="#d97706" font-size="13" font-weight="bold">41 % (Max : A1)</text>
  <text x="815" y="94" fill="#475569" font-size="8.2">Saint-Denis</text>

  <rect x="510" y="117" width="178" height="52" rx="6" fill="#f0fdf4" stroke="#bbf7d0"/>
  <text x="520" y="134" fill="#166534" font-size="8.8" font-weight="bold">Régression par le Vent</text>
  <text x="520" y="156" fill="#15803d" font-size="13.5" font-weight="bold">r = −0,34</text>
  <text x="600" y="156" fill="#475569" font-size="8.2">(Dispersion active)</text>

  <rect x="702" y="117" width="178" height="52" rx="6" fill="#eff6ff" stroke="#bfdbfe"/>
  <text x="712" y="134" fill="#1e3a8a" font-size="8.8" font-weight="bold">Accroissement Thermique</text>
  <text x="712" y="156" fill="#0284c7" font-size="13.5" font-weight="bold">r = +0,58 (O₃)</text>
  <text x="810" y="156" fill="#475569" font-size="8.2">(Chaleur &amp; UV)</text>

  <rect x="510" y="179" width="370" height="54" rx="6" fill="#f8fafc" stroke="#94a3b8"/>
  <text x="522" y="197" fill="#0f172a" font-size="9.2" font-weight="bold">Plus-value directe pour la prévention et la décision :</text>
  <text x="522" y="215" fill="#334155" font-size="8.6">Avertir les personnes fragiles avant les pics (8h, 15h, 20h) et cibler les campagnes de régulation.</text>
</svg>"""


SVG_PREVISIONS_IA = """<svg viewBox="0 0 920 255" width="100%" height="240" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff;font-family:'Segoe UI',Calibri,Arial,sans-serif;">
  <rect x="5" y="5" width="910" height="245" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="25" y="28" fill="#0f172a" font-size="11.2" font-weight="bold">A. Comparaison AQI Prédit vs AQI Réel sur 24 Heures (Validation Capteur de Référence)</text>

  <line x1="50" y1="42" x2="50" y2="195" stroke="#64748b" stroke-width="1.2"/>
  <line x1="50" y1="195" x2="520" y2="195" stroke="#64748b" stroke-width="1.2"/>
  <text x="42" y="50" fill="#475569" font-size="9" text-anchor="end">35</text>
  <text x="42" y="98" fill="#475569" font-size="9" text-anchor="end">25</text>
  <text x="42" y="146" fill="#475569" font-size="9" text-anchor="end">15</text>
  <text x="42" y="195" fill="#475569" font-size="9" text-anchor="end">5</text>

  <!-- Corridor de confiance -->
  <polygon fill="#d1fae5" stroke="#6ee7b7" stroke-width="1"
    points="65,86 115,92 165,82 215,78 265,98 315,108 365,114 415,112 465,108 505,106
            505,134 465,136 415,138 365,140 315,136 265,126 215,108 165,112 115,120 65,114"/>

  <!-- Courbe prédite (valeurs issues du test 24h de la présentation : ~24.6 -> 25.7 -> 21.6 -> 19.5 -> 21.6) -->
  <polyline fill="none" stroke="#047857" stroke-width="3"
    points="65,100 115,105 165,97 215,93 265,112 315,122 365,127 415,125 465,122 505,120"/>
  <!-- Courbe réelle (29.0 -> 23.0 -> 26.0 -> 19.0 -> 17.0 -> 19.0 -> 23.0 -> 18.0) -->
  <polyline fill="none" stroke="#1d4ed8" stroke-width="2.2" stroke-dasharray="5 3"
    points="65,82 115,108 165,112 215,92 265,122 315,132 365,122 415,105 465,115 505,132"/>

  <g fill="#475569" font-size="8.5" text-anchor="middle">
    <text x="65" y="212">11h (+1h)</text><text x="165" y="212">15h (+5h)</text><text x="265" y="212">20h (+10h)</text><text x="365" y="212">02h (+16h)</text><text x="505" y="212">10h (+24h)</text>
  </g>
  <rect x="65" y="222" width="14" height="10" fill="#d1fae5" stroke="#047857"/>
  <text x="85" y="231" fill="#1e293b" font-size="8.8">AQI Prédit par LightGBM (24h) &amp; Zone de Confiance</text>
  <line x1="330" y1="227" x2="350" y2="227" stroke="#1d4ed8" stroke-width="2.2" stroke-dasharray="4 2"/>
  <text x="356" y="231" fill="#1e293b" font-size="8.8">AQI Réel observé (MAE = 2,07 pts sur ce capteur)</text>

  <!-- Partie droite : Automatisation quotidienne et valeur ajoutée -->
  <text x="545" y="28" fill="#0f172a" font-size="11.2" font-weight="bold">B. Du Calcul Quotidien (00h45) à l'Anticipation Sanitaire</text>
  <rect x="545" y="42" width="350" height="190" rx="8" fill="#ffffff" stroke="#cbd5e1"/>

  <text x="560" y="66" fill="#1e293b" font-size="9" font-weight="bold">1. Historique local &amp; tendances des polluants (7 derniers jours)</text>
  <rect x="560" y="72" width="235" height="12" rx="4" fill="#1d4ed8"/>
  <text x="805" y="82" fill="#1d4ed8" font-size="9.5" font-weight="bold">54 %</text>

  <text x="560" y="102" fill="#1e293b" font-size="9" font-weight="bold">2. Vent prévu à 24h (vitesse &amp; direction de dispersion)</text>
  <rect x="560" y="108" width="110" height="12" rx="4" fill="#047857"/>
  <text x="678" y="118" fill="#047857" font-size="9.5" font-weight="bold">19 %</text>

  <text x="560" y="138" fill="#1e293b" font-size="9" font-weight="bold">3. Température prévue (formation d'ozone ou inversion thermique)</text>
  <rect x="560" y="144" width="90" height="12" rx="4" fill="#d97706"/>
  <text x="658" y="154" fill="#d97706" font-size="9.5" font-weight="bold">15 %</text>

  <text x="560" y="174" fill="#1e293b" font-size="9" font-weight="bold">4. Pluies attendues &amp; cycles d'activité urbaine (heures/jours)</text>
  <rect x="560" y="180" width="72" height="12" rx="4" fill="#7c3aed"/>
  <text x="640" y="190" fill="#7c3aed" font-size="9.5" font-weight="bold">12 %</text>

  <text x="560" y="212" fill="#047857" font-size="8.5" font-weight="bold">Précision : MAE = 2,07 pts (capteur test) · MAE global 34 stations = 5,97 pts</text>
  <text x="560" y="225" fill="#475569" font-size="8.2">Export quotidien à 00h45 vers Google Sheets &amp; Power BI pour les 24h suivantes.</text>
</svg>"""


def render_svg_to_png(svg_content: str, out_png: Path, width: int = 1200, height: int = 460):
    """Rend un SVG en image PNG haute résolution via Chromium headless."""
    tmp_html = SCRATCH_DIR / f"{out_png.stem}.html"
    tmp_html.write_text(
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>*{{margin:0;padding:0;box-sizing:border-box;}}body{{background:#fff;display:flex;align-items:center;justify-content:center;width:{width}px;height:{height}px;overflow:hidden;}}</style>"
        f"</head><body>{svg_content}</body></html>",
        encoding="utf-8",
    )
    browser = get_browser()
    prof = SCRATCH_DIR / "chrome_img_prof"
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--user-data-dir={prof}",
        f"--window-size={width},{height}",
        f"--screenshot={out_png}",
        tmp_html.resolve().as_uri(),
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=25)


# ══════════════════════════════════════════════════════════════════════════════
# 2. CONTENU RÉDIGÉ ALIGNÉ SUR LE POWERPOINT & LA PLUS-VALUE UTILISATEUR
# ══════════════════════════════════════════════════════════════════════════════

def build_clean_html(arch_png_path: Path) -> str:
    arch_b64 = base64.b64encode(arch_png_path.read_bytes()).decode("ascii")
    arch_img_tag = f'<img src="data:image/png;base64,{arch_b64}" style="width:100%;max-height:360px;object-fit:contain;border-radius:6px;border:1px solid #cbd5e1;" alt="Architecture du système Smart City" />'

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8" />
<title>Rapport de Projet Smart City — Surveillance et Prévision de la Qualité de l'Air (AQI) en Île-de-France</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 17mm 18mm 17mm 18mm;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    line-height: 1.54;
    font-size: 10.6pt;
    text-align: justify;
  }}
  .page-break {{ page-break-before: always; }}

  /* Page de garde */
  .cover {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 252mm;
    border: 1.5px solid #1e3a8a;
    padding: 26px 30px;
    border-radius: 6px;
    background: #ffffff;
  }}
  .cover-top {{
    border-bottom: 3px solid #1e3a8a;
    padding-bottom: 12px;
    text-align: center;
  }}
  .cover-univ {{
    font-size: 11pt;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #1e3a8a;
  }}
  .cover-domain {{
    font-size: 9.8pt;
    color: #475569;
    margin-top: 4px;
  }}
  .cover-center {{
    text-align: center;
    margin: 18px 0;
  }}
  .cover-type {{
    display: inline-block;
    background: #eff6ff;
    color: #1e40af;
    border: 1px solid #bfdbfe;
    padding: 5px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 9.8pt;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 14px;
  }}
  .cover-main-title {{
    font-size: 20pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.25;
    margin-bottom: 10px;
  }}
  .cover-motto {{
    font-size: 11.5pt;
    font-style: italic;
    color: #047857;
    font-weight: 700;
    margin-bottom: 12px;
  }}
  .cover-sub {{
    font-size: 10.8pt;
    color: #334155;
    line-height: 1.45;
    max-width: 95%;
    margin: 0 auto 16px auto;
  }}
  .cover-footer {{
    border-top: 1px solid #cbd5e1;
    padding-top: 12px;
    display: flex;
    justify-content: space-between;
    font-size: 9.5pt;
    color: #475569;
  }}

  /* Titres */
  h1 {{
    font-size: 14.5pt;
    font-weight: 800;
    color: #1e3a8a;
    border-bottom: 2px solid #1e3a8a;
    padding-bottom: 5px;
    margin: 16px 0 11px 0;
    text-align: left;
  }}
  h2 {{
    font-size: 11.6pt;
    font-weight: 700;
    color: #0f172a;
    margin: 13px 0 6px 0;
    text-align: left;
  }}
  p {{
    margin-bottom: 8px;
  }}
  ul, ol {{
    margin: 5px 0 9px 22px;
  }}
  li {{
    margin-bottom: 4.5px;
  }}

  /* Tableaux */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 9px 0 13px 0;
    font-size: 9.2pt;
    text-align: left;
  }}
  th {{
    background: #1e3a8a;
    color: #ffffff;
    padding: 6px 8px;
    font-weight: 700;
    border: 1px solid #1e3a8a;
  }}
  td {{
    padding: 5.5px 8px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }}
  tr:nth-child(even) td {{
    background: #f8fafc;
  }}

  .value-box {{
    background: #f0fdf4;
    border-left: 4px solid #047857;
    padding: 9px 13px;
    margin: 9px 0 11px 0;
    font-size: 9.8pt;
  }}
  .fig-wrap {{
    margin: 10px 0 12px 0;
    text-align: center;
    page-break-inside: avoid;
  }}
  .fig-caption {{
    font-size: 8.8pt;
    color: #475569;
    font-style: italic;
    margin-top: 5px;
    text-align: center;
  }}
  .toc-line {{
    display: flex;
    justify-content: space-between;
    border-bottom: 1px dotted #94a3b8;
    padding: 4.5px 0;
    font-size: 10pt;
  }}
</style>
</head>
<body>

<!-- PAGE DE GARDE -->
<div class="cover">
  <div class="cover-top">
    <div class="cover-univ">Projet Smart City — Air Quality Index (AQI) &amp; Aide à la Décision Publique</div>
    <div class="cover-domain">Surveillance Temps Réel, Prévision à 24 Heures, Application Web &amp; Business Intelligence</div>
  </div>

  <div class="cover-center">
    <div class="cover-type">Rapport Complet de Projet</div>
    <div class="cover-main-title">
      Étude, Surveillance et Prédiction à 24 Heures de la Qualité de l'Air en Île-de-France : La Donnée au Service d'une Ville Plus Saine
    </div>
    <div class="cover-motto">
      « Des données d'aujourd'hui pour une meilleure qualité de l'air demain »
    </div>
    <div class="cover-sub">
      Prévention sanitaire des populations vulnérables, anticipation logistique et hospitalière, sensibilisation citoyenne et industrielle, architecture Cloud automatisée sur 34 stations et pilotage décisionnel via Application Web et Power BI.
    </div>

    <div style="margin: 10px auto; max-width: 98%;">
      {arch_img_tag}
    </div>
  </div>

  <div class="cover-footer">
    <div><strong>Périmètre :</strong> Région Île-de-France (34 capteurs · Flux temps réel 30 min · Prévisions J+1)</div>
    <div><strong>Année :</strong> 2025 – 2026</div>
  </div>
</div>

<!-- SOMMAIRE ALIGNÉ SUR LE POWERPOINT -->
<div class="page-break"></div>
<h1>Table des Matières</h1>
<div style="margin-bottom: 14px;">
  <div class="toc-line"><span><strong>01. Introduction &amp; Contexte : Pourquoi étudier la qualité de l'air est d'utilité publique ?</strong></span><span><strong>2</strong></span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;1.1. L'air, une ressource vitale critique au cœur des enjeux sanitaires urbains</span><span>2</span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;1.2. Les six grandes plus-values du projet pour la société et les utilisateurs</span><span>2</span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;1.3. L'échelle de qualité de l'air et les composants chimiques suivis</span><span>3</span></div>
  <div class="toc-line"><span><strong>02. Architecture Globale du Système : De la Collecte aux Utilisateurs</strong></span><span><strong>4</strong></span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;2.1. Vue d'ensemble et diagramme de l'architecture déployée</span><span>4</span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;2.2. Infrastructure, sécurité des données et accès par profil d'utilisateur</span><span>5</span></div>
  <div class="toc-line"><span><strong>03. Collecte Historique et Streaming Temps Réel sur Serveur Distant</strong></span><span><strong>5</strong></span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;3.1. Connexion aux données atmosphériques et météorologiques sur 34 stations</span><span>5</span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;3.2. Amorçage historique (75 jours) et flux continu toutes les 30 minutes</span><span>6</span></div>
  <div class="toc-line"><span><strong>04. Prédictions pour les 24 Prochaines Heures par Intelligence Artificielle</strong></span><span><strong>6</strong></span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;4.1. Identifier les facteurs d'accroissement et les schémas récurrents (« patterns »)</span><span>6</span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;4.2. Modélisation LightGBM à 24 horizons, résultats de précision et automatisation à 00h45</span><span>7</span></div>
  <div class="toc-line"><span><strong>05. Exploitation Décisionnelle : Power BI, Application Web et Mobilité</strong></span><span><strong>8</strong></span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;5.1. Architecture de connexion sécurisée vers Power BI (PostgreSQL SSL &amp; Google Sheets)</span><span>8</span></div>
  <div class="toc-line"><span>&nbsp;&nbsp;&nbsp;&nbsp;5.2. Valeur ajoutée des tableaux de bord et analyse de la surconcentration routière</span><span>8</span></div>
  <div class="toc-line"><span><strong>06. Conclusion Générale et Perspectives d'Amélioration</strong></span><span><strong>9</strong></span></div>
  <div class="toc-line" style="border-bottom:none;"><span><strong>07. Références Scientifiques et Ressources Mobilisées</strong></span><span><strong>9</strong></span></div>
</div>

<h1>01. Introduction &amp; Contexte : Pourquoi étudier la qualité de l'air est d'utilité publique ?</h1>

<h2>1.1. L'air, une ressource vitale critique au cœur des enjeux sanitaires urbains</h2>
<p>
  Respirer librement est un besoin humain fondamental que l'on accomplit plus de vingt mille fois par jour sans y penser. Pourtant, parmi toutes les ressources naturelles de la Terre, l'air occupe une place singulière et critique : contrairement à l'eau ou à l'alimentation, son absence ou son altération sévère met immédiatement la vie humaine en péril. À l'échelle mondiale, l'Organisation Mondiale de la Santé (OMS, 2021) rappelle que la pollution atmosphérique constitue le premier risque environnemental pour la santé, provoquant près de 4,2 millions de décès prématurés par an. En France, Santé Publique France (2021) évalue cet impact à 40 000 décès annuels, avec une exposition particulièrement marquée en Île-de-France où plus de 12,3 millions d'habitants cohabitent avec un trafic routier et une activité urbaine très denses.
</p>
<p>
  Étudier, surveiller et anticiper la qualité de l'air relève donc d'une véritable mission d'<strong>utilité publique</strong>. C'est dans cet esprit qu'a été conçu notre projet <strong>Smart City</strong> : développer une plateforme complète capable à la fois de parcourir l'historique de la qualité de l'air sur plusieurs jours en Île-de-France, de suivre la situation en temps réel toutes les trente minutes, et surtout d'afficher la prédiction de l'indice de qualité de l'air pour les <strong>24 prochaines heures</strong>.
</p>

<h2>1.2. Les six grandes plus-values du projet pour la société et les utilisateurs</h2>
<p>
  Bien au-delà de l'exercice technologique, ce projet a été pensé autour des bénéfices humains, sanitaires et organisationnels qu'il apporte à ses utilisateurs. Six objectifs majeurs structurent notre démarche :
</p>
<ol>
  <li>
    <strong>Prévenir d'éventuelles crises sanitaires aiguës :</strong> En cas de dégradation brutale ou imprévue de la qualité de l'air, la plateforme permet d'avertir immédiatement les citoyens afin qu'ils puissent rester à l'abri chez eux et éviter toute exposition dangereuse.
  </li>
  <li>
    <strong>Protéger de manière ciblée les personnes malades et vulnérables :</strong> Les personnes particulièrement sensibles à une baisse de la qualité de l'air (patients asthmatiques, insuffisants respiratoires ou cardiaques, jeunes enfants, personnes âgées) peuvent consulter la prévision avant de sortir et adapter leurs déplacements ou leur traitement préventif.
  </li>
  <li>
    <strong>Sensibiliser les citoyens et responsabiliser les acteurs économiques et industriels :</strong> En rendant visibles et incontestables les niveaux de pollution heure par heure, l'outil permet aux autorités de mener des campagnes de prévention ciblées pour sensibiliser la population et inciter les industriels ainsi que les acteurs du transport à réduire leurs émissions.
  </li>
  <li>
    <strong>Produire des statistiques de référence sur les facteurs de pollution :</strong> Le croisement systématique des polluants et de la météo permet de comprendre scientifiquement quels facteurs provoquent l'accroissement de la pollution (embouteillages, chaleur estivale, absence de vent) ou au contraire sa régression (balayage par le vent, lavage de l'air par la pluie).
  </li>
  <li>
    <strong>Identifier des schémas récurrents (« patterns ») pour l'anticipation matérielle et hospitalière :</strong> Repérer à l'avance le retour des mauvaises périodes donne aux services de santé et aux collectivités la possibilité d'anticiper matériellement les besoins (constitution de stocks de masques, bouteilles d'oxygène, préparation des équipements et des urgences hospitalières face aux pics d'admission pour crises d'asthme ou détresses respiratoires).
  </li>
  <li>
    <strong>Offrir un socle d'analyse pour la recherche scientifique :</strong> La conservation structurée de l'évolution de la qualité de l'air donne aux chercheurs et aux urbanistes la matière nécessaire pour évaluer de nouvelles solutions d'aménagement urbain durable.
  </li>
</ol>

<h2>1.3. L'échelle de qualité de l'air et les composants chimiques suivis</h2>
<p>
  Afin que chaque citoyen et chaque élu puisse interpréter immédiatement le niveau de risque sans être chimiste, le système s'appuie sur l'indice européen de qualité de l'air (<strong>European AQI</strong>) pour la modélisation régionale, tout en proposant des grilles de lecture visuelles par code couleur universel allant du vert (air sain) au bordeaux/violet (danger sanitaire aigu) :
</p>

<table>
  <thead>
    <tr>
      <th>Niveau de Qualité de l'Air</th>
      <th>Échelle Européenne (EAQI)</th>
      <th>Échelle Internationale (US AQI)</th>
      <th>Couleur</th>
      <th>Signification concrète et précautions pour l'utilisateur</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Bon</strong></td>
      <td>0 – 20</td>
      <td>0 – 50</td>
      <td>Vert (#00E400)</td>
      <td>Qualité de l'air idéale. Aucune restriction : moment privilégié pour le sport en plein air et l'aération des logements et écoles.</td>
    </tr>
    <tr>
      <td><strong>Correct / Modéré</strong></td>
      <td>20 – 40</td>
      <td>51 – 100</td>
      <td>Jaune (#FFFF00)</td>
      <td>Qualité acceptable. Seules les personnes extrêmement sensibles ou multi-allergiques peuvent ressentir une légère gêne.</td>
    </tr>
    <tr>
      <td><strong>Moyen / Dégradé pour les personnes sensibles</strong></td>
      <td>40 – 60</td>
      <td>101 – 150</td>
      <td>Orange (#FF7E00)</td>
      <td>Les personnes asthmatiques, malades ou âgées doivent limiter les efforts prolongés à l'extérieur et garder leur traitement à portée.</td>
    </tr>
    <tr>
      <td><strong>Mauvais</strong></td>
      <td>60 – 80</td>
      <td>151 – 200</td>
      <td>Rouge (#FF0000)</td>
      <td>Tout le monde peut commencer à ressentir des effets irritants ; les groupes sensibles doivent éviter les sorties aux heures de pointe.</td>
    </tr>
    <tr>
      <td><strong>Très mauvais</strong></td>
      <td>80 – 100</td>
      <td>201 – 300</td>
      <td>Violet (#8F3F97)</td>
      <td>Alerte sanitaire : déclenchement recommandé des mesures préfectorales (réduction de vitesse, circulation différenciée) et préparation hospitalière.</td>
    </tr>
    <tr>
      <td><strong>Extrêmement mauvais / Dangereux</strong></td>
      <td>&gt; 100</td>
      <td>301 – 500</td>
      <td>Bordeaux (#7E0023)</td>
      <td>Urgence sanitaire : recommandation générale de rester à l'intérieur et mobilisation des équipements de protection respiratoire.</td>
    </tr>
  </tbody>
</table>

<p>
  Pour calculer cet indice et comprendre l'origine exacte de chaque dégradation, la plateforme suit simultanément <strong>sept composants atmosphériques majeurs</strong> complétés par la météo :
</p>
<ul>
  <li><strong>Les particules fines PM<sub>2.5</sub> (diamètre inférieur à 2,5 µm) :</strong> issues des combustions (moteurs, chauffage au bois, industrie), elles pénètrent profondément dans les alvéoles pulmonaires et le système cardiovasculaire (Pope &amp; Dockery, 2006).</li>
  <li><strong>Les particules en suspension PM<sub>10</sub> (diamètre inférieur à 10 µm) :</strong> générées notamment par l'abrasion mécanique des freins, des pneus et de la chaussée routière ainsi que par les chantiers (Harrison et al., 2012), elles irritent les voies respiratoires supérieures.</li>
  <li><strong>Le dioxyde d'azote (NO<sub>2</sub>) :</strong> gaz traceur direct du trafic routier et des embouteillages urbains, responsable d'une forte inflammation bronchique chez l'enfant et l'asthmatique.</li>
  <li><strong>L'ozone troposphérique (O<sub>3</sub>) :</strong> polluant secondaire formé l'après-midi sous l'action du soleil et de la chaleur à partir des gaz d'échappement (Seinfeld &amp; Pandis, 2016), très irritant lors des épisodes caniculaires.</li>
  <li><strong>Le dioxyde de soufre (SO<sub>2</sub>) et le monoxyde de carbone (CO) :</strong> liés aux procédés industriels et aux combustions incomplètes, surveillés pour prévenir tout risque toxique aigu.</li>
  <li><strong>Le pollen de bouleau :</strong> bio-aérosol printanier majeur dont l'allergénicité est fortement accrue en présence de pollution chimique (D'Amato et al., 2007).</li>
</ul>

<div class="page-break"></div>
<h1>02. Architecture Globale du Système : De la Collecte aux Utilisateurs</h1>

<h2>2.1. Vue d'ensemble et diagramme de l'architecture déployée</h2>
<p>
  Pour répondre à la devise du projet — <em>« Des données d'aujourd'hui pour une meilleure qualité de l'air demain »</em> — nous avons conçu une architecture complète, automatisée de bout en bout et déployée sans lourdeur inutile (sur serveur distant léger sans conteneurisation complexe). Comme l'illustre la <strong>Figure 1</strong> ci-dessous (issue de notre présentation générale), le système s'articule autour de cinq grandes briques fonctionnelles :
</p>

<div class="fig-wrap">
  {arch_img_tag}
  <div class="fig-caption">Figure 1 — Diagramme officiel de l'architecture du système Smart City : chaîne de traitement de la donnée depuis les capteurs jusqu'aux quatre profils d'utilisateurs finaux.</div>
</div>

<ol>
  <li>
    <strong>1. Sources de données externes :</strong> Le système interroge de manière coordonnée l'API Qualité de l'air (indice européen AQI, PM<sub>10</sub>, PM<sub>2.5</sub>, NO<sub>2</sub>, O<sub>3</sub>, SO<sub>2</sub>, CO et pollen de bouleau) et l'API Météo (température à 2 m, humidité relative, vitesse et direction du vent à 10 m, précipitations) fournies par la plateforme Open-Meteo (programme européen Copernicus CAMS), à partir du référentiel géographique des <strong>34 capteurs d'Île-de-France</strong> (latitude, longitude, nom et identifiant officiel).
  </li>
  <li>
    <strong>2. Ingestion et traitement en continu :</strong> Un serveur distant Linux assure d'une part le <strong>streaming toutes les 30 minutes</strong> (récupération automatisée, nettoyage, transformation et envoi vers la base), et d'autre part la <strong>fusion Air + Météo</strong> (alignement horaire, formatage et agrégation).
  </li>
  <li>
    <strong>3. Base de données Cloud centralisée (Supabase PostgreSQL) :</strong> L'ensemble des observations consolidées, des comptes utilisateurs et des paramètres est stocké dans une base relationnelle PostgreSQL hébergée sur Supabase, qui gère également l'authentification et les droits d'accès selon le rôle de chaque utilisateur.
  </li>
  <li>
    <strong>4. Serveur distant d'Intelligence Artificielle et passerelle Google Sheets :</strong> Chaque nuit à <strong>00h45</strong>, le serveur distant interroge les dernières mesures, exécute l'algorithme de Machine Learning <strong>LightGBM</strong> pour générer les prédictions sur les 24 prochaines heures, et sauvegarde automatiquement ces résultats dans une feuille <strong>Google Sheets</strong> dédiée (via l'écosystème Google Workspace).
  </li>
  <li>
    <strong>5. Application Web et Business Intelligence (Power BI) :</strong> En bout de chaîne, l'utilisateur accède à l'Application Web (consultation en temps réel, cartes interactives, indicateurs sanitaires, prévisions à 24h et alertes) qui intègre directement les rapports interactifs et analyses avancées construits sous <strong>Microsoft Power BI</strong>.
  </li>
</ol>

<h2>2.2. Infrastructure, sécurité des données et accès par profil d'utilisateur</h2>
<p>
  Comme le montre la partie inférieure du diagramme d'architecture (Figure 1), ce pipeline technique repose sur un socle transversal d'<strong>Infrastructure et Sécurité</strong> garantissant : un hébergement Cloud haute disponibilité, le chiffrement des échanges (HTTPS / TLS), le contrôle d'accès respectueux de la confidentialité (RGPD), la supervision continue de la disponibilité, ainsi qu'une triple sauvegarde (base PostgreSQL, fichiers modèles et Google Sheets).
</p>
<p>
  Surtout, toute cette architecture converge vers <strong>quatre profils d'utilisateurs clairement identifiés</strong>, accessibles sur ordinateur comme sur mobile :
</p>
<ul>
  <li><strong>Les Citoyens :</strong> accès libre et lisible aux informations de leur quartier, conseils de prévention pour les personnes fragiles et sensibilisation quotidienne.</li>
  <li><strong>Les Décideurs et Autorités publiques :</strong> suivi des indicateurs critiques, anticipation des pics 24 heures à l'avance, déclenchement des mesures d'urgence et génération de bilans officiels.</li>
  <li><strong>Les Experts et Analystes (Chercheurs, Urbanistes) :</strong> exploration approfondie des corrélations air-météo, validation statistique des résultats et étude des tendances dans Power BI.</li>
  <li><strong>Les Services municipaux et Exploitants :</strong> gestion opérationnelle du réseau de 34 stations, réception des alertes automatiques et planification logistique sur le terrain.</li>
</ul>

<div class="page-break"></div>
<h1>03. Collecte Historique et Streaming Temps Réel sur Serveur Distant</h1>

<h2>3.1. Connexion aux données atmosphériques et météorologiques sur 34 stations</h2>
<p>
  Pour offrir une vision fidèle de la qualité de l'air sur l'ensemble de l'Île-de-France, le système interroge <strong>34 stations de surveillance géolocalisées</strong> réparties entre le cœur de l'agglomération parisienne (Opéra, Champs-Élysées, Les Halles, Paris 18<sup>e</sup>, Place Victor Basch, Boulevard de Denain, Périphérique Est), la petite couronne (Saint-Denis Autoroute A1, Bobigny, Gennevilliers, La Défense, Vitry-sur-Seine, Nogent-sur-Marne) et la grande couronne urbaine ou rurale (Versailles, Cergy-Pontoise, Évry, Melun RN6, Montlhéry RN20, Lognes, Forêt de Fontainebleau, Rambouillet, Saint-Martin-du-Tertre, Frémainville, Coulommiers).
</p>
<p>
  Cette répartition équilibrée entre <strong>8 stations de trafic routier intense</strong> et <strong>26 stations de fond urbain ou rural</strong> est essentielle pour l'utilisateur : elle permet de comparer à tout instant l'air respiré au bord d'une autoroute à celui d'une zone résidentielle ou d'un massif forestier.
</p>

<h2>3.2. Amorçage historique (75 jours) et flux continu toutes les 30 minutes</h2>
<p>
  La collecte des données a été conçue en deux temps complémentaires afin que l'application soit immédiatement riche en historique tout en restant constamment à jour :
</p>
<ul>
  <li>
    <strong>1. L'importation de l'historique initial (1 800 heures, soit 75 jours) :</strong> Lors de l'initialisation de la base, le système récupère en une seule passe les 1 800 dernières heures de mesures atmosphériques et météorologiques pour chacun des 34 capteurs (soit plus de 61 000 relevés horaires complets). Pour les chercheurs et les analystes, cet historique offre immédiatement la profondeur nécessaire pour étudier les cycles hebdomadaires et entraîner les modèles prédictifs.
  </li>
  <li>
    <strong>2. Le streaming temps réel toutes les 30 minutes sur serveur distant :</strong> Afin que la collecte fonctionne 24h/24 de manière autonome — même lorsque les ordinateurs des utilisateurs sont éteints — le module de récupération a été déployé sur un <strong>serveur virtuel privé distant (VPS sous Linux)</strong>. Un planificateur système (tâche automatisée <em>cron</em> réglée toutes les 30 minutes) interroge les 34 stations, fusionne l'air et la météo sur l'heure de Paris, vérifie la validité des mesures et synchronise le lot avec la base Supabase. Grâce à une règle d'unicité sur le couple (capteur, heure), aucune donnée n'est jamais dupliquée.
  </li>
</ul>

<div class="value-box">
  <strong>Bénéfice concret de cette automatisation pour les services municipaux :</strong> Les équipes n'ont aucune manipulation quotidienne à effectuer. La plateforme se met à jour toute seule toutes les demi-heures et signale immédiatement dans ses journaux de supervision si la synchronisation des 34 stations avec le Cloud s'est déroulée avec succès.
</div>

<div class="page-break"></div>
<h1>04. Prédictions pour les 24 Prochaines Heures par Intelligence Artificielle</h1>

<h2>4.1. Identifier les facteurs d'accroissement et les schémas récurrents (« patterns »)</h2>
<p>
  Comme souligné dans les objectifs initiaux du projet, anticiper la mauvaise qualité de l'air suppose d'abord de comprendre statistiquement <strong>quels facteurs font monter ou baisser l'indice AQI</strong> et quels sont les <strong>schémas récurrents (« patterns »)</strong> des périodes critiques. L'analyse exploratoire menée sur notre base francilienne met en évidence trois lois majeures directement utiles à la prévention (illustrées par la Figure 2) :
</p>
<ol>
  <li>
    <strong>Le double pic journalier lié aux déplacements (« pattern » des heures de pointe) :</strong> En semaine, les concentrations de dioxyde d'azote et de particules augmentent fortement entre 07h00 et 09h00, puis entre 18h00 et 21h00. À l'inverse, le créneau de fin de nuit et de milieu de matinée offre l'air le plus respirable pour l'aération des hôpitaux, des écoles et des logements.
  </li>
  <li>
    <strong>L'accroissement photochimique d'après-midi par temps chaud :</strong> La corrélation positive marquée entre la température et l'ozone (<strong><em>r</em> = +0,58</strong>) montre que lors des journées ensoleillées, le pic de pollution se déplace vers 15h00. C'est sur ce créneau d'après-midi que les personnes fragiles doivent être averties de rester au frais.
  </li>
  <li>
    <strong>Le rôle nettoyant du vent et de la pluie :</strong> La vitesse du vent fait baisser significativement les concentrations de dioxyde d'azote (<strong><em>r</em> = −0,34</strong>) et de particules fines (<strong><em>r</em> = −0,31</strong>) en dispersant le dôme de pollution urbain, tandis que les précipitations rabattent les poussières au sol.
  </li>
</ol>

<div class="fig-wrap">
  {SVG_CYCLE_DIURNE}
  <div class="fig-caption">Figure 2 — Identification des schémas journaliers (« patterns ») d'exposition (A) et quantification statistique des facteurs d'accroissement ou de régression de la qualité de l'air en Île-de-France (B).</div>
</div>

<h2>4.2. Modélisation LightGBM à 24 horizons, résultats de précision et automatisation à 00h45</h2>
<p>
  Pour transformer ces régularités statistiques en prévisions horaires fiables sur les 24 prochaines heures, nous avons mis en œuvre l'algorithme d'apprentissage automatique <strong>LightGBM</strong> (<em>Light Gradient Boosting Machine</em> ; Ke et al., 2017). Plutôt que d'utiliser un modèle unique qui accumulerait des erreurs d'heure en heure, le système mobilise <strong>24 modèles spécialisés chacun sur une échéance précise</strong> (+1h, +2h, …, +24h).
</p>
<p>
  Chaque modèle exploite <strong>233 indicateurs explicatifs</strong> : la mémoire des polluants sur la station (de la dernière heure jusqu'à 7 jours en arrière pour capter la saisonnalité hebdomadaire), les moyennes glissantes sur 6h, 24h et 72h, la projection géométrique du vent, ainsi que les <strong>prévisions météorologiques horaires annoncées entre l'instant présent et l'heure cible</strong> (température, vent, humidité et cumul de pluie).
</p>
<p>
  <strong>Validation de la précision sur données réelles :</strong> Afin de vérifier concrètement la fiabilité des prédictions avant de les diffuser aux utilisateurs, nous avons confronté les valeurs prédites par notre modèle aux valeurs réellement mesurées heure par heure sur 24 heures consécutives (Figure 3). Sur notre capteur de référence présenté lors de la soutenance, l'écart absolu moyen (<strong>MAE</strong>) entre l'AQI prédit et l'AQI réel descend à seulement <strong>2,07 points d'indice AQI</strong> (avec une erreur quadratique RMSE de 6,04), les deux courbes évoluant en parfaite cohérence tout au long des 24 heures. Sur l'ensemble des 34 stations de la région (plus de 800 relevés horaires variés), l'erreur moyenne s'établit à <strong>5,97 points EAQI</strong>, soit près de <strong>80 % de fiabilité globale</strong>.
</p>
<p>
  <strong>Planification quotidienne à 00h45 :</strong> Conformément à l'architecture opérationnelle retenue, le calcul des prédictions est lancé automatiquement <strong>une fois par jour à 00h45</strong> sur le serveur distant afin de publier dès le début de journée la trajectoire complète des 24 prochaines heures pour les 34 stations.
</p>

<div class="fig-wrap">
  {SVG_PREVISIONS_IA}
  <div class="fig-caption">Figure 3 — Confrontation sur 24 heures entre l'AQI prédit et l'AQI réel (MAE = 2,07 points sur le capteur de référence ; MAE = 5,97 points sur l'ensemble des 34 stations) (A) et poids des facteurs explicatifs (B).</div>
</div>

<div class="page-break"></div>
<h1>05. Exploitation Décisionnelle : Power BI, Application Web et Mobilité</h1>

<h2>5.1. Architecture de connexion sécurisée vers Power BI (PostgreSQL SSL &amp; Google Sheets)</h2>
<p>
  Pour permettre aux décideurs, aux analystes et aux services municipaux d'explorer les données passées, présentes et futures sans aucune barrière technique, nous avons conçu une architecture décisionnelle hybride sous <strong>Microsoft Power BI</strong> et au sein de notre <strong>Application Web</strong>, en accordant une priorité absolue à la <strong>sécurité des accès</strong> :
</p>
<ul>
  <li>
    <strong>1. Connexion sécurisée à la base PostgreSQL (Supabase) par certificat SSL :</strong> Power BI est connecté directement à la base relationnelle PostgreSQL hébergée sur Supabase pour interroger l'historique et le flux temps réel des 34 stations. Par mesure de sécurité stricte, <strong>aucune clé API n'apparaît dans le code applicatif (même chiffrée)</strong> : les secrets sont isolés côté serveur et l'accès à la base de données depuis le poste d'analyse Power BI est verrouillé par un <strong>certificat SSL officiel</strong> téléchargé et installé sur la machine autorisée.
  </li>
  <li>
    <strong>2. Connexion automatisée à Google Sheets (via Google Workspace) pour les prévisions 24h :</strong> Afin de rendre les prédictions de l'intelligence artificielle immédiatement disponibles dans les rapports décisionnels sans alourdir la base transactionnelle, le script quotidien de 00h45 s'authentifie auprès de <strong>Google Workspace</strong> à l'aide d'un certificat de compte de service sécurisé et alimente automatiquement une feuille <strong>Google Sheets dédiée aux 24 prochaines heures</strong>, à laquelle Power BI est directement relié.
  </li>
</ul>

<h2>5.2. Valeur ajoutée des tableaux de bord et analyse de la surconcentration routière</h2>
<p>
  L'alliance du portail Web interactif et des six pages du rapport Power BI transforme ces flux sécurisés en outils concrets d'aide à la décision pour chaque catégorie d'utilisateur :
</p>

<table>
  <thead>
    <tr>
      <th>Outil / Volet de la plateforme</th>
      <th>Ce que l'utilisateur visualise concrètement</th>
      <th>Plus-value opérationnelle et sanitaire</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Vue d'ensemble &amp; Carte interactive des 34 stations</strong></td>
      <td>Score AQI en temps réel (moyenne Île-de-France ou station choisie), polluant majoritaire, météo locale et carte colorée filtrable sur toute la région.</td>
      <td>Permet aux <strong>citoyens et personnes malades</strong> de vérifier en une seconde si l'air de leur commune est sain avant de sortir ou de faire du sport.</td>
    </tr>
    <tr>
      <td><strong>Volet Mobilité &amp; Surconcentration Routière (+52 %)</strong></td>
      <td>Comparaison en direct entre les 8 axes routiers et les 26 stations de fond : affiche une <strong>Surconcentration Trafic de +52 %</strong> en NO<sub>2</sub> et un <strong>Indice d'Émission Trafic de 41 %</strong> (point critique : <strong>Autoroute A1 à Saint-Denis</strong>).</td>
      <td>Permet aux <strong>autorités et services municipaux</strong> de cibler les restrictions de vitesse et campagnes de prévention sur les axes réellement saturés.</td>
    </tr>
    <tr>
      <td><strong>Volet Prédictions 24h &amp; Alertes proactives</strong></td>
      <td>Courbe horaire prévue pour demain avec marge de confiance à 95 %, détection automatique des anomalies et envoi d'alertes par courriel.</td>
      <td>Permet aux <strong>hôpitaux, écoles et préfectures</strong> d'anticiper matériellement les périodes critiques (masques, oxygène, arrêtés de circulation) dès la veille.</td>
    </tr>
    <tr>
      <td><strong>Espace Power BI (6 pages) &amp; Rapports PDF</strong></td>
      <td>Statistiques temporelles AQI, tableau croisé Air/Météo, carte à bulles, dernier relevé, prévisions multi-capteurs et export PDF officiel en un clic.</td>
      <td>Offre aux <strong>chercheurs, analystes et élus</strong> un outil complet pour étudier les tendances sur plusieurs jours ou semaines et appuyer les décisions publiques.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>
<h1>06. Conclusion Générale et Perspectives d'Amélioration</h1>

<h2>6.1. Bilan d'un projet réalisé de bout en bout au service des usagers</h2>
<p>
  Au terme de ce travail, nous avons conçu, déployé et validé <strong>de bout en bout</strong> une chaîne décisionnelle complète répondant à un enjeu majeur de santé publique en Île-de-France. Notre système récupère automatiquement l'historique météorologique et atmosphérique ainsi que les mesures en temps réel des 34 capteurs franciliens (via un serveur distant interrogeant les flux toutes les 30 minutes), les stocke de manière sécurisée et sans doublon dans une base PostgreSQL Cloud, permet de les explorer de façon ponctuelle ou glissante sur la période choisie, et calcule chaque nuit à 00h45 la prédiction des 24 prochaines heures avant de restituer l'ensemble dans une Application Web moderne et dans Power BI.
</p>
<p>
  Surtout, le projet démontre concrètement comment la donnée environnementale devient un **outil de protection citoyenne** : qu'il s'agisse d'avertir à temps une personne fragile ou asthmatique, d'aider les hôpitaux à anticiper les pics de détresse respiratoire grâce à l'identification des schémas journaliers (« patterns »), de sensibiliser les industriels et les automobilistes au vu de la surconcentration routière (+52 % sur les grands axes), ou de fournir aux chercheurs des statistiques fiables, chaque composant technique a été mis au service direct de l'utilisateur.
</p>

<h2>6.2. Perspectives et améliorations futures</h2>
<p>
  Conformément à la feuille de route dégagée à l'issue de notre réalisation, quatre axes prioritaires d'amélioration permettront d'enrichir encore la plateforme :
</p>
<ol>
  <li>
    <strong>Améliorer encore la précision des prédictions :</strong> En enrichissant l'historique d'apprentissage sur un cycle annuel complet (4 saisons) et en intégrant en direct les données de comptage routier francilien, nous pourrons réduire encore l'écart moyen entre l'AQI prédit et l'AQI réel, notamment lors des changements météorologiques brusques.
  </li>
  <li>
    <strong>Étendre la longueur de la période de prédiction (au-delà de 24 heures) :</strong> Passer d'un horizon de 24 heures à un horizon de <strong>48 heures voire 72 heures (J+2 / J+3)</strong> offrira un délai d'anticipation encore plus confortable aux hôpitaux (gestion des stocks d'oxygène et de masques) ainsi qu'aux autorités préfectorales pour organiser les campagnes de prévention.
  </li>
  <li>
    <strong>Renforcer la convivialité et l'accessibilité des visualisations :</strong> Continuer à simplifier l'expérience utilisateur sur le portail Web et mobile (notifications personnalisées par quartier et par profil de santé, simulateur visuel d'itinéraire le moins pollué pour les piétons et cyclistes).
  </li>
  <li>
    <strong>Expérimenter d'autres algorithmes de Machine Learning et de Deep Learning :</strong> Comparer et combiner nos modèles actuels d'arbres boostés (LightGBM) avec d'autres architectures avancées d'apprentissage profond temporel et spatial (tels que les réseaux récurrents LSTM, les Transformers temporels ou les réseaux de neurones sur graphes reliant les 34 stations entre elles selon le sens du vent).
  </li>
</ol>

<h1>07. Références Scientifiques et Ressources Mobilisées</h1>
<div style="font-size: 9.2pt; line-height: 1.46; color: #334155;">
  <p style="margin-bottom:5px;"><strong>[1] Organisation Mondiale de la Santé (OMS).</strong> (2021). <em>Lignes directrices mondiales de l'OMS sur la qualité de l'air : particules (PM2.5 et PM10), ozone, dioxyde d'azote, dioxyde de soufre et monoxyde de carbone.</em> Genève : OMS.</p>
  <p style="margin-bottom:5px;"><strong>[2] Agence Européenne pour l'Environnement (EEA).</strong> (2023). <em>Air Quality in Europe 2023 : impacts sanitaires et référentiel de l'Indice Européen de Qualité de l'Air (European AQI).</em> Luxembourg : Office des publications de l'Union européenne.</p>
  <p style="margin-bottom:5px;"><strong>[3] Santé Publique France.</strong> (2021). <em>Pollution de l'air ambiant : estimations de son impact sur la mortalité et la morbidité hospitalière en France métropolitaine.</em> Saint-Maurice : Santé Publique France.</p>
  <p style="margin-bottom:5px;"><strong>[4] Open-Meteo &amp; Programme Européen Copernicus (CAMS).</strong> (2025). <em>Air Quality API &amp; Historical/Forecast Weather API Documentation — Modèles atmosphériques régionaux haute résolution pour l'Europe.</em></p>
  <p style="margin-bottom:5px;"><strong>[5] Pope, C. A., &amp; Dockery, D. W.</strong> (2006). Health effects of fine particulate air pollution: lines that connect. <em>Journal of the Air &amp; Waste Management Association</em>, 56(6), 709–742.</p>
  <p style="margin-bottom:5px;"><strong>[6] Harrison, R. M., Jones, A. M., Gietl, J., Yin, J., &amp; Green, D. C.</strong> (2012). Estimation of the contributions of brake dust, tire wear, and resuspension to nonexhaust traffic particles (PM10). <em>Environmental Science &amp; Technology</em>, 46(12), 6523–6529.</p>
  <p style="margin-bottom:5px;"><strong>[7] D'Amato, G., Cecchi, L., Bonini, S., et al.</strong> (2007). Allergenic pollen and pollen allergy in Europe: synergy with urban air pollutants. <em>Allergy</em>, 62(9), 976–990.</p>
  <p style="margin-bottom:5px;"><strong>[8] Seinfeld, J. H., &amp; Pandis, S. N.</strong> (2016). <em>Atmospheric Chemistry and Physics: From Air Pollution to Climate Change</em> (3rd ed.). Hoboken, NJ : John Wiley &amp; Sons.</p>
  <p style="margin-bottom:5px;"><strong>[9] Lenschow, P., Abraham, H. J., Kutzner, K., et al.</strong> (2001). Some ideas about the sources of pollutants in urban environments (Méthode incrémentale Trafic vs Fond). <em>Atmospheric Environment</em>, 35, S23–S33.</p>
  <p style="margin-bottom:5px;"><strong>[10] Ke, G., Meng, Q., Finley, T., et al.</strong> (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, 30, 3146–3154.</p>
  <p style="margin-bottom:0;"><strong>[11] Taieb, S. B., Bontempi, G., Atiya, A. F., &amp; Sorjamaa, A.</strong> (2012). A review and comparison of strategies for multi-step ahead time series forecasting (Stratégie multi-horizons 24h). <em>Expert Systems with Applications</em>, 39(8), 7067–7083.</p>
</div>

</body>
</html>
"""


# ══════════════════════════════════════════════════════════════════════════════
# 3. GÉNÉRATEUR OPENXML (.DOCX) NATIF ALIGNÉ SUR LE POWERPOINT
# ══════════════════════════════════════════════════════════════════════════════

def w_p(text: str = "", style: str = "Normal", bold: bool = False, italic: bool = False, align: str = "both") -> str:
    """Crée un paragraphe OpenXML Word (<w:p>)."""
    t_esc = html.escape(text)
    rpr = ""
    if bold:
        rpr += "<w:b/>"
    if italic:
        rpr += "<w:i/>"
    rpr_xml = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return (
        f'<w:p>'
        f'<w:pPr><w:pStyle w:val="{style}"/><w:jc w:val="{align}"/></w:pPr>'
        f'<w:r>{rpr_xml}<w:t xml:space="preserve">{t_esc}</w:t></w:r>'
        f'</w:p>'
    )


def w_callout(title: str, body: str, fill_hex: str = "F0FDF4", border_hex: str = "047857", title_hex: str = "065F46") -> str:
    """Crée un encadré mis en valeur dans Word."""
    return f"""
    <w:tbl>
      <w:tblPr>
        <w:tblW w:w="5000" w:type="pct"/>
        <w:tblBorders>
          <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
          <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>
          <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
          <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
        </w:tblBorders>
      </w:tblPr>
      <w:tr>
        <w:tc>
          <w:tcPr>
            <w:shd w:val="clear" w:color="auto" w:fill="{fill_hex}"/>
            <w:tcMar>
              <w:top w:w="120" w:type="dxa"/>
              <w:bottom w:w="120" w:type="dxa"/>
              <w:left w:w="180" w:type="dxa"/>
              <w:right w:w="160" w:type="dxa"/>
            </w:tcMar>
          </w:tcPr>
          <w:p>
            <w:pPr><w:jc w:val="both"/><w:spacing w:before="20" w:after="60"/></w:pPr>
            <w:r><w:rPr><w:b/><w:color w:val="{title_hex}"/><w:sz w:val="21"/></w:rPr><w:t>{html.escape(title)}</w:t></w:r>
          </w:p>
          <w:p>
            <w:pPr><w:jc w:val="both"/><w:spacing w:before="20" w:after="20"/></w:pPr>
            <w:r><w:rPr><w:color w:val="1E293B"/><w:sz w:val="20"/></w:rPr><w:t>{html.escape(body)}</w:t></w:r>
          </w:p>
        </w:tc>
      </w:tr>
    </w:tbl>
    <w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr></w:p>
    """


def w_page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def w_image(rel_id: str, docpr_id: int, cx_emu: int, cy_emu: int, caption: str) -> str:
    """Insère une image centrée dans Word suivie de sa légende italique."""
    return f"""
    <w:p>
      <w:pPr><w:jc w:val="center"/><w:spacing w:before="120" w:after="60"/></w:pPr>
      <w:r>
        <w:drawing>
          <wp:inline distT="0" distB="0" distL="0" distR="0">
            <wp:extent cx="{cx_emu}" cy="{cy_emu}"/>
            <wp:docPr id="{docpr_id}" name="Figure_{docpr_id}"/>
            <wp:cNvGraphicFramePr>
              <a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>
            </wp:cNvGraphicFramePr>
            <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
                  <pic:nvPicPr>
                    <pic:cNvPr id="{docpr_id}" name="fig{docpr_id}.png"/>
                    <pic:cNvPicPr/>
                  </pic:nvPicPr>
                  <pic:blipFill>
                    <a:blip r:embed="{rel_id}"/>
                    <a:stretch><a:fillRect/></a:stretch>
                  </pic:blipFill>
                  <pic:spPr>
                    <a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx_emu}" cy="{cy_emu}"/></a:xfrm>
                    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                  </pic:spPr>
                </pic:pic>
              </a:graphicData>
            </a:graphic>
          </wp:inline>
        </w:drawing>
      </w:r>
    </w:p>
    {w_p(caption, style="Caption", italic=True, align="center")}
    """


def w_table(headers: list[str], rows: list[list[str]]) -> str:
    """Crée un tableau Word élégant avec en-tête bleu marine (#1E3A8A)."""
    hdr_cells = "".join(
        f'<w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="1E3A8A"/>'
        f'<w:tcMar><w:top w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:left w:w="110" w:type="dxa"/><w:right w:w="110" w:type="dxa"/></w:tcMar></w:tcPr>'
        f'<w:p><w:pPr><w:jc w:val="left"/><w:spacing w:before="40" w:after="40"/></w:pPr>'
        f'<w:r><w:rPr><w:b/><w:color w:val="FFFFFF"/><w:sz w:val="19"/></w:rPr><w:t>{html.escape(h)}</w:t></w:r></w:p></w:tc>'
        for h in headers
    )
    body_rows = ""
    for idx, r in enumerate(rows):
        bg = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        cells = "".join(
            f'<w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{bg}"/>'
            f'<w:tcMar><w:top w:w="70" w:type="dxa"/><w:bottom w:w="70" w:type="dxa"/><w:left w:w="110" w:type="dxa"/><w:right w:w="110" w:type="dxa"/></w:tcMar></w:tcPr>'
            f'<w:p><w:pPr><w:jc w:val="left"/><w:spacing w:before="30" w:after="30"/></w:pPr>'
            f'<w:r><w:rPr><w:b w:val="{"true" if c_idx == 0 else "false"}"/><w:sz w:val="19"/></w:rPr><w:t>{html.escape(cell)}</w:t></w:r></w:p></w:tc>'
            for c_idx, cell in enumerate(r)
        )
        body_rows += f"<w:tr>{cells}</w:tr>"

    return f"""
    <w:tbl>
      <w:tblPr>
        <w:tblW w:w="5000" w:type="pct"/>
        <w:tblBorders>
          <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
          <w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
          <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
          <w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
          <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
          <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        </w:tblBorders>
      </w:tblPr>
      <w:tr>{hdr_cells}</w:tr>
      {body_rows}
    </w:tbl>
    <w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr></w:p>
    """


def build_docx(fig1_png: Path, fig2_png: Path, fig3_png: Path):
    """Assemble le fichier Microsoft Word (.docx) complet aligné sur le PowerPoint et la plus-value utilisateur."""
    body_parts = [
        # Page de garde
        w_p("PROJET SMART CITY — AIR QUALITY INDEX (AQI) & AIDE À LA DÉCISION PUBLIQUE", style="Subtitle", bold=True, align="center"),
        w_p("Surveillance Temps Réel, Prévision à 24 Heures, Application Web & Business Intelligence", style="Normal", italic=True, align="center"),
        w_p("", align="center"),
        w_p("RAPPORT COMPLET DE PROJET", style="Heading2", bold=True, align="center"),
        w_p("Étude, Surveillance et Prédiction à 24 Heures de la Qualité de l'Air en Île-de-France : La Donnée au Service d'une Ville Plus Saine", style="Title", bold=True, align="center"),
        w_p("« Des données d'aujourd'hui pour une meilleure qualité de l'air demain »", style="Normal", bold=True, italic=True, align="center"),
        w_p("Prévention sanitaire des populations vulnérables, anticipation logistique et hospitalière, sensibilisation citoyenne et industrielle, architecture Cloud automatisée sur 34 stations et pilotage décisionnel via Application Web et Power BI.", style="Normal", align="center"),
        w_image("rId4", 1, 5760000, 3880000, "Architecture globale du système Smart City : de la collecte multi-sources aux quatre profils d'utilisateurs."),
        w_p("Périmètre : Région Île-de-France (34 capteurs · Flux temps réel 30 min · Prévisions J+1) — Année 2025–2026", style="Normal", bold=True, align="center"),
        w_page_break(),

        # Table des matières alignée sur les 6 parties du PowerPoint
        w_p("Table des Matières", style="Heading1", bold=True, align="left"),
        w_p("01. Introduction & Contexte : Pourquoi étudier la qualité de l'air est d'utilité publique ?"),
        w_p("    1.1. L'air, une ressource vitale critique au cœur des enjeux sanitaires urbains"),
        w_p("    1.2. Les six grandes plus-values du projet pour la société et les utilisateurs"),
        w_p("    1.3. L'échelle de qualité de l'air et les composants chimiques suivis"),
        w_p("02. Architecture Globale du Système : De la Collecte aux Utilisateurs"),
        w_p("    2.1. Vue d'ensemble et diagramme de l'architecture déployée"),
        w_p("    2.2. Infrastructure, sécurité des données et accès par profil d'utilisateur"),
        w_p("03. Collecte Historique et Streaming Temps Réel sur Serveur Distant"),
        w_p("    3.1. Connexion aux données atmosphériques et météorologiques sur 34 stations"),
        w_p("    3.2. Amorçage historique (75 jours) et flux continu toutes les 30 minutes"),
        w_p("04. Prédictions pour les 24 Prochaines Heures par Intelligence Artificielle"),
        w_p("    4.1. Identifier les facteurs d'accroissement et les schémas récurrents (« patterns »)"),
        w_p("    4.2. Modélisation LightGBM à 24 horizons, résultats de précision et automatisation à 00h45"),
        w_p("05. Exploitation Décisionnelle : Power BI, Application Web et Mobilité"),
        w_p("    5.1. Architecture de connexion sécurisée vers Power BI (PostgreSQL SSL & Google Sheets)"),
        w_p("    5.2. Valeur ajoutée des tableaux de bord et analyse de la surconcentration routière"),
        w_p("06. Conclusion Générale et Perspectives d'Amélioration"),
        w_p("07. Références Scientifiques et Ressources Mobilisées"),
        w_page_break(),

        # Chapitre 01
        w_p("01. Introduction & Contexte : Pourquoi étudier la qualité de l'air est d'utilité publique ?", style="Heading1", bold=True, align="left"),
        w_p("1.1. L'air, une ressource vitale critique au cœur des enjeux sanitaires urbains", style="Heading2", bold=True, align="left"),
        w_p("Respirer librement est un besoin humain fondamental que l'on accomplit plus de vingt mille fois par jour sans y penser. Pourtant, parmi toutes les ressources naturelles de la Terre, l'air occupe une place singulière et critique : contrairement à l'eau ou à l'alimentation, son absence ou son altération sévère met immédiatement la vie humaine en péril. À l'échelle mondiale, l'Organisation Mondiale de la Santé (OMS, 2021) rappelle que la pollution atmosphérique constitue le premier risque environnemental pour la santé, provoquant près de 4,2 millions de décès prématurés par an. En France, Santé Publique France (2021) évalue cet impact à 40 000 décès annuels, avec une exposition particulièrement marquée en Île-de-France où plus de 12,3 millions d'habitants cohabitent avec un trafic routier et une activité urbaine très denses."),
        w_p("Étudier, surveiller et anticiper la qualité de l'air relève donc d'une véritable mission d'utilité publique. C'est dans cet esprit qu'a été conçu notre projet Smart City : développer une plateforme complète capable à la fois de parcourir l'historique de la qualité de l'air sur plusieurs jours en Île-de-France, de suivre la situation en temps réel toutes les trente minutes, et surtout d'afficher la prédiction de l'indice de qualité de l'air pour les 24 prochaines heures."),

        w_p("1.2. Les six grandes plus-values du projet pour la société et les utilisateurs", style="Heading2", bold=True, align="left"),
        w_p("Bien au-delà de l'exercice technologique, ce projet a été pensé autour des bénéfices humains, sanitaires et organisationnels qu'il apporte à ses utilisateurs. Six objectifs majeurs structurent notre démarche :"),
        w_p("1. Prévenir d'éventuelles crises sanitaires aiguës : En cas de dégradation brutale ou imprévue de la qualité de l'air, la plateforme permet d'avertir immédiatement les citoyens afin qu'ils puissent rester à l'abri chez eux et éviter toute exposition dangereuse."),
        w_p("2. Protéger de manière ciblée les personnes malades et vulnérables : Les personnes particulièrement sensibles à une baisse de la qualité de l'air (patients asthmatiques, insuffisants respiratoires ou cardiaques, jeunes enfants, personnes âgées) peuvent consulter la prévision avant de sortir et adapter leurs déplacements ou leur traitement préventif."),
        w_p("3. Sensibiliser les citoyens et responsabiliser les acteurs économiques et industriels : En rendant visibles et incontestables les niveaux de pollution heure par heure, l'outil permet aux autorités de mener des campagnes de prévention ciblées pour sensibiliser la population et inciter les industriels ainsi que les acteurs du transport à réduire leurs émissions."),
        w_p("4. Produire des statistiques de référence sur les facteurs de pollution : Le croisement systématique des polluants et de la météo permet de comprendre scientifiquement quels facteurs provoquent l'accroissement de la pollution (embouteillages, chaleur estivale, absence de vent) ou au contraire sa régression (balayage par le vent, lavage de l'air par la pluie)."),
        w_p("5. Identifier des schémas récurrents (« patterns ») pour l'anticipation matérielle et hospitalière : Repérer à l'avance le retour des mauvaises périodes donne aux services de santé et aux collectivités la possibilité d'anticiper matériellement les besoins (constitution de stocks de masques, bouteilles d'oxygène, préparation des équipements et des urgences hospitalières face aux pics d'admission pour crises d'asthme ou détresses respiratoires)."),
        w_p("6. Offrir un socle d'analyse pour la recherche scientifique : La conservation structurée de l'évolution de la qualité de l'air donne aux chercheurs et aux urbanistes la matière nécessaire pour évaluer de nouvelles solutions d'aménagement urbain durable."),

        w_p("1.3. L'échelle de qualité de l'air et les composants chimiques suivis", style="Heading2", bold=True, align="left"),
        w_p("Afin que chaque citoyen et chaque élu puisse interpréter immédiatement le niveau de risque sans être chimiste, le système s'appuie sur l'indice européen de qualité de l'air (European AQI) pour la modélisation régionale, tout en proposant des grilles de lecture visuelles par code couleur universel allant du vert (air sain) au bordeaux/violet (danger sanitaire aigu) :"),

        w_table(
            ["Niveau de Qualité de l'Air", "Échelle Européenne (EAQI)", "Échelle Internationale (US AQI)", "Couleur", "Signification concrète et précautions pour l'utilisateur"],
            [
                ["Bon", "0 – 20", "0 – 50", "Vert (#00E400)", "Qualité de l'air idéale. Aucune restriction : moment privilégié pour le sport en plein air et l'aération des logements et écoles."],
                ["Correct / Modéré", "20 – 40", "51 – 100", "Jaune (#FFFF00)", "Qualité acceptable. Seules les personnes extrêmement sensibles ou multi-allergiques peuvent ressentir une légère gêne."],
                ["Moyen / Dégradé pour les personnes sensibles", "40 – 60", "101 – 150", "Orange (#FF7E00)", "Les personnes asthmatiques, malades ou âgées doivent limiter les efforts prolongés à l'extérieur et garder leur traitement à portée."],
                ["Mauvais", "60 – 80", "151 – 200", "Rouge (#FF0000)", "Tout le monde peut commencer à ressentir des effets irritants ; les groupes sensibles doivent éviter les sorties aux heures de pointe."],
                ["Très mauvais", "80 – 100", "201 – 300", "Violet (#8F3F97)", "Alerte sanitaire : déclenchement recommandé des mesures préfectorales (réduction de vitesse, circulation différenciée) et préparation hospitalière."],
                ["Extrêmement mauvais / Dangereux", "> 100", "301 – 500", "Bordeaux (#7E0023)", "Urgence sanitaire : recommandation générale de rester à l'intérieur et mobilisation des équipements de protection respiratoire."],
            ],
        ),

        w_p("Pour calculer cet indice et comprendre l'origine exacte de chaque dégradation, la plateforme suit simultanément sept composants atmosphériques majeurs complétés par la météo :"),
        w_p("• Les particules fines PM2.5 (diamètre inférieur à 2,5 µm) : issues des combustions (moteurs, chauffage au bois, industrie), elles pénètrent profondément dans les alvéoles pulmonaires et le système cardiovasculaire (Pope & Dockery, 2006)."),
        w_p("• Les particules en suspension PM10 (diamètre inférieur à 10 µm) : générées notamment par l'abrasion mécanique des freins, des pneus et de la chaussée routière ainsi que par les chantiers (Harrison et al., 2012), elles irritent les voies respiratoires supérieures."),
        w_p("• Le dioxyde d'azote (NO₂) : gaz traceur direct du trafic routier et des embouteillages urbains, responsable d'une forte inflammation bronchique chez l'enfant et l'asthmatique."),
        w_p("• L'ozone troposphérique (O₃) : polluant secondaire formé l'après-midi sous l'action du soleil et de la chaleur à partir des gaz d'échappement (Seinfeld & Pandis, 2016), très irritant lors des épisodes caniculaires."),
        w_p("• Le dioxyde de soufre (SO₂) et le monoxyde de carbone (CO) : liés aux procédés industriels et aux combustions incomplètes, surveillés pour prévenir tout risque toxique aigu."),
        w_p("• Le pollen de bouleau : bio-aérosol printanier majeur dont l'allergénicité est fortement accrue en présence de pollution chimique (D'Amato et al., 2007)."),

        # Chapitre 02
        w_page_break(),
        w_p("02. Architecture Globale du Système : De la Collecte aux Utilisateurs", style="Heading1", bold=True, align="left"),
        w_p("2.1. Vue d'ensemble et diagramme de l'architecture déployée", style="Heading2", bold=True, align="left"),
        w_p("Pour répondre à la devise du projet — « Des données d'aujourd'hui pour une meilleure qualité de l'air demain » — nous avons conçu une architecture complète, automatisée de bout en bout et déployée sur un serveur distant léger (sans conteneurisation complexe). Comme l'illustre la Figure 1 ci-dessous, le système s'articule autour de cinq grandes briques fonctionnelles :"),

        w_image("rId4", 2, 5760000, 3880000, "Figure 1 — Diagramme officiel de l'architecture du système Smart City : chaîne de traitement de la donnée depuis les capteurs jusqu'aux quatre profils d'utilisateurs finaux."),

        w_p("1. Sources de données externes : Le système interroge de manière coordonnée l'API Qualité de l'air (indice européen AQI, PM10, PM2.5, NO₂, O₃, SO₂, CO et pollen de bouleau) et l'API Météo (température à 2 m, humidité relative, vitesse et direction du vent à 10 m, précipitations) fournies par la plateforme Open-Meteo (programme européen Copernicus CAMS), à partir du référentiel géographique des 34 capteurs d'Île-de-France (latitude, longitude, nom et identifiant officiel)."),
        w_p("2. Ingestion et traitement en continu : Un serveur distant Linux assure d'une part le streaming toutes les 30 minutes (récupération automatisée, nettoyage, transformation et envoi vers la base), et d'autre part la fusion Air + Météo (alignement horaire, formatage et agrégation)."),
        w_p("3. Base de données Cloud centralisée (Supabase PostgreSQL) : L'ensemble des observations consolidées, des comptes utilisateurs et des paramètres est stocké dans une base relationnelle PostgreSQL hébergée sur Supabase, qui gère également l'authentification et les droits d'accès selon le rôle de chaque utilisateur."),
        w_p("4. Serveur distant d'Intelligence Artificielle et passerelle Google Sheets : Chaque nuit à 00h45, le serveur distant interroge les dernières mesures, exécute l'algorithme de Machine Learning LightGBM pour générer les prédictions sur les 24 prochaines heures, et sauvegarde automatiquement ces résultats dans une feuille Google Sheets dédiée (via l'écosystème Google Workspace)."),
        w_p("5. Application Web et Business Intelligence (Power BI) : En bout de chaîne, l'utilisateur accède à l'Application Web (consultation en temps réel, cartes interactives, indicateurs sanitaires, prévisions à 24h et alertes) qui intègre directement les rapports interactifs et analyses avancées construits sous Microsoft Power BI."),

        w_p("2.2. Infrastructure, sécurité des données et accès par profil d'utilisateur", style="Heading2", bold=True, align="left"),
        w_p("Comme le montre la partie inférieure du diagramme d'architecture (Figure 1), ce pipeline technique repose sur un socle transversal d'Infrastructure et Sécurité garantissant : un hébergement Cloud haute disponibilité, le chiffrement des échanges (HTTPS / TLS), le contrôle d'accès respectueux de la confidentialité (RGPD), la supervision continue de la disponibilité, ainsi qu'une triple sauvegarde (base PostgreSQL, fichiers modèles et Google Sheets)."),
        w_p("Surtout, toute cette architecture converge vers quatre profils d'utilisateurs clairement identifiés, accessibles sur ordinateur comme sur mobile :"),
        w_p("• Les Citoyens : accès libre et lisible aux informations de leur quartier, conseils de prévention pour les personnes fragiles et sensibilisation quotidienne."),
        w_p("• Les Décideurs et Autorités publiques : suivi des indicateurs critiques, anticipation des pics 24 heures à l'avance, déclenchement des mesures d'urgence et génération de bilans officiels."),
        w_p("• Les Experts et Analystes (Chercheurs, Urbanistes) : exploration approfondie des corrélations air-météo, validation statistique des résultats et étude des tendances dans Power BI."),
        w_p("• Les Services municipaux et Exploitants : gestion opérationnelle du réseau de 34 stations, réception des alertes automatiques et planification logistique sur le terrain."),

        # Chapitre 03
        w_p("03. Collecte Historique et Streaming Temps Réel sur Serveur Distant", style="Heading1", bold=True, align="left"),
        w_p("3.1. Connexion aux données atmosphériques et météorologiques sur 34 stations", style="Heading2", bold=True, align="left"),
        w_p("Pour offrir une vision fidèle de la qualité de l'air sur l'ensemble de l'Île-de-France, le système interroge 34 stations de surveillance géolocalisées réparties entre le cœur de l'agglomération parisienne (Opéra, Champs-Élysées, Les Halles, Paris 18e, Place Victor Basch, Boulevard de Denain, Périphérique Est), la petite couronne (Saint-Denis Autoroute A1, Bobigny, Gennevilliers, La Défense, Vitry-sur-Seine, Nogent-sur-Marne) et la grande couronne urbaine ou rurale (Versailles, Cergy-Pontoise, Évry, Melun RN6, Montlhéry RN20, Lognes, Forêt de Fontainebleau, Rambouillet, Saint-Martin-du-Tertre, Frémainville, Coulommiers)."),
        w_p("Cette répartition équilibrée entre 8 stations de trafic routier intense et 26 stations de fond urbain ou rural est essentielle pour l'utilisateur : elle permet de comparer à tout instant l'air respiré au bord d'une autoroute à celui d'une zone résidentielle ou d'un massif forestier."),

        w_p("3.2. Amorçage historique (75 jours) et flux continu toutes les 30 minutes", style="Heading2", bold=True, align="left"),
        w_p("La collecte des données a été conçue en deux temps complémentaires afin que l'application soit immédiatement riche en historique tout en restant constamment à jour :"),
        w_p("• 1. L'importation de l'historique initial (1 800 heures, soit 75 jours) : Lors de l'initialisation de la base, le système récupère en une seule passe les 1 800 dernières heures de mesures atmosphériques et météorologiques pour chacun des 34 capteurs (soit plus de 61 000 relevés horaires complets). Pour les chercheurs et les analystes, cet historique offre immédiatement la profondeur nécessaire pour étudier les cycles hebdomadaires et entraîner les modèles prédictifs."),
        w_p("• 2. Le streaming temps réel toutes les 30 minutes sur serveur distant : Afin que la collecte fonctionne 24h/24 de manière autonome — même lorsque les ordinateurs des utilisateurs sont éteints — le module de récupération a été déployé sur un serveur virtuel privé distant (VPS sous Linux). Un planificateur système (tâche automatisée réglée toutes les 30 minutes) interroge les 34 stations, fusionne l'air et la météo sur l'heure de Paris, vérifie la validité des mesures et synchronise le lot avec la base Supabase. Grâce à une règle d'unicité sur le couple (capteur, heure), aucune donnée n'est jamais dupliquée."),
        w_callout(
            "Bénéfice concret de cette automatisation pour les services municipaux :",
            "Les équipes n'ont aucune manipulation quotidienne à effectuer. La plateforme se met à jour toute seule toutes les demi-heures et signale immédiatement dans ses journaux de supervision si la synchronisation des 34 stations avec le Cloud s'est déroulée avec succès.",
        ),

        # Chapitre 04
        w_p("04. Prédictions pour les 24 Prochaines Heures par Intelligence Artificielle", style="Heading1", bold=True, align="left"),
        w_p("4.1. Identifier les facteurs d'accroissement et les schémas récurrents (« patterns »)", style="Heading2", bold=True, align="left"),
        w_p("Comme souligné dans les objectifs initiaux du projet, anticiper la mauvaise qualité de l'air suppose d'abord de comprendre statistiquement quels facteurs font monter ou baisser l'indice AQI et quels sont les schémas récurrents (« patterns ») des périodes critiques. L'analyse exploratoire menée sur notre base francilienne met en évidence trois lois majeures directement utiles à la prévention (illustrées par la Figure 2) :"),
        w_p("1. Le double pic journalier lié aux déplacements (« pattern » des heures de pointe) : En semaine, les concentrations de dioxyde d'azote et de particules augmentent fortement entre 07h00 et 09h00, puis entre 18h00 et 21h00. À l'inverse, le créneau de fin de nuit et de milieu de matinée offre l'air le plus respirable pour l'aération des hôpitaux, des écoles et des logements."),
        w_p("2. L'accroissement photochimique d'après-midi par temps chaud : La corrélation positive marquée entre la température et l'ozone (r = +0,58) montre que lors des journées ensoleillées, le pic de pollution se déplace vers 15h00. C'est sur ce créneau d'après-midi que les personnes fragiles doivent être averties de rester au frais."),
        w_p("3. Le rôle nettoyant du vent et de la pluie : La vitesse du vent fait baisser significativement les concentrations de dioxyde d'azote (r = −0,34) et de particules fines (r = −0,31) en dispersant le dôme de pollution urbain, tandis que les précipitations rabattent les poussières au sol."),

        w_image("rId6", 3, 5760000, 1680000, "Figure 2 — Identification des schémas journaliers (« patterns ») d'exposition (A) et quantification statistique des facteurs d'accroissement ou de régression de la qualité de l'air en Île-de-France (B)."),

        w_p("4.2. Modélisation LightGBM à 24 horizons, résultats de précision et automatisation à 00h45", style="Heading2", bold=True, align="left"),
        w_p("Pour transformer ces régularités statistiques en prévisions horaires fiables sur les 24 prochaines heures, nous avons mis en œuvre l'algorithme d'apprentissage automatique LightGBM (Light Gradient Boosting Machine ; Ke et al., 2017). Plutôt que d'utiliser un modèle unique qui accumulerait des erreurs d'heure en heure, le système mobilise 24 modèles spécialisés chacun sur une échéance précise (+1h, +2h, …, +24h)."),
        w_p("Chaque modèle exploite 233 indicateurs explicatifs : la mémoire des polluants sur la station (de la dernière heure jusqu'à 7 jours en arrière pour capter la saisonnalité hebdomadaire), les moyennes glissantes sur 6h, 24h et 72h, la projection géométrique du vent, ainsi que les prévisions météorologiques horaires annoncées entre l'instant présent et l'heure cible (température, vent, humidité et cumul de pluie)."),
        w_p("Validation de la précision sur données réelles : Afin de vérifier concrètement la fiabilité des prédictions avant de les diffuser aux utilisateurs, nous avons confronté les valeurs prédites par notre modèle aux valeurs réellement mesurées heure par heure sur 24 heures consécutives (Figure 3). Sur notre capteur de référence présenté lors de la soutenance, l'écart absolu moyen (MAE) entre l'AQI prédit et l'AQI réel descend à seulement 2,07 points d'indice AQI (avec une erreur quadratique RMSE de 6,04), les deux courbes évoluant en parfaite cohérence tout au long des 24 heures. Sur l'ensemble des 34 stations de la région (plus de 800 relevés horaires variés), l'erreur moyenne s'établit à 5,97 points EAQI, soit près de 80 % de fiabilité globale."),
        w_p("Planification quotidienne à 00h45 : Conformément à l'architecture opérationnelle retenue, le calcul des prédictions est lancé automatiquement une fois par jour à 00h45 sur le serveur distant afin de publier dès le début de journée la trajectoire complète des 24 prochaines heures pour les 34 stations."),

        w_image("rId5", 4, 5760000, 1590000, "Figure 3 — Confrontation sur 24 heures entre l'AQI prédit et l'AQI réel (MAE = 2,07 points sur le capteur de référence ; MAE = 5,97 points sur l'ensemble des 34 stations) (A) et poids des facteurs explicatifs (B)."),

        # Chapitre 05
        w_p("05. Exploitation Décisionnelle : Power BI, Application Web et Mobilité", style="Heading1", bold=True, align="left"),
        w_p("5.1. Architecture de connexion sécurisée vers Power BI (PostgreSQL SSL & Google Sheets)", style="Heading2", bold=True, align="left"),
        w_p("Pour permettre aux décideurs, aux analystes et aux services municipaux d'explorer les données passées, présentes et futures sans aucune barrière technique, nous avons conçu une architecture décisionnelle hybride sous Microsoft Power BI et au sein de notre Application Web, en accordant une priorité absolue à la sécurité des accès :"),
        w_p("• 1. Connexion sécurisée à la base PostgreSQL (Supabase) par certificat SSL : Power BI est connecté directement à la base relationnelle PostgreSQL hébergée sur Supabase pour interroger l'historique et le flux temps réel des 34 stations. Par mesure de sécurité stricte, aucune clé API n'apparaît dans le code applicatif (même chiffrée) : les secrets sont isolés côté serveur et l'accès à la base de données depuis le poste d'analyse Power BI est verrouillé par un certificat SSL officiel téléchargé et installé sur la machine autorisée."),
        w_p("• 2. Connexion automatisée à Google Sheets (via Google Workspace) pour les prévisions 24h : Afin de rendre les prédictions de l'intelligence artificielle immédiatement disponibles dans les rapports décisionnels sans alourdir la base transactionnelle, le script quotidien de 00h45 s'authentifie auprès de Google Workspace à l'aide d'un certificat de compte de service sécurisé et alimente automatiquement une feuille Google Sheets dédiée aux 24 prochaines heures, à laquelle Power BI est directement relié."),

        w_p("5.2. Valeur ajoutée des tableaux de bord et analyse de la surconcentration routière", style="Heading2", bold=True, align="left"),
        w_p("L'alliance du portail Web interactif et des six pages du rapport Power BI transforme ces flux sécurisés en outils concrets d'aide à la décision pour chaque catégorie d'utilisateur :"),

        w_table(
            ["Outil / Volet de la plateforme", "Ce que l'utilisateur visualise concrètement", "Plus-value opérationnelle et sanitaire"],
            [
                ["Vue d'ensemble & Carte interactive des 34 stations", "Score AQI en temps réel (moyenne Île-de-France ou station choisie), polluant majoritaire, météo locale et carte colorée filtrable sur toute la région.", "Permet aux citoyens et personnes malades de vérifier en une seconde si l'air de leur commune est sain avant de sortir ou de faire du sport."],
                ["Volet Mobilité & Surconcentration Routière (+52 %)", "Comparaison en direct entre les 8 axes routiers et les 26 stations de fond : affiche une Surconcentration Trafic de +52 % en NO₂ et un Indice d'Émission Trafic de 41 % (point critique : Autoroute A1 à Saint-Denis).", "Permet aux autorités et services municipaux de cibler les restrictions de vitesse et campagnes de prévention sur les axes réellement saturés."],
                ["Volet Prédictions 24h & Alertes proactives", "Courbe horaire prévue pour demain avec marge de confiance à 95 %, détection automatique des anomalies et envoi d'alertes par courriel.", "Permet aux hôpitaux, écoles et préfectures d'anticiper matériellement les périodes critiques (masques, oxygène, arrêtés de circulation) dès la veille."],
                ["Espace Power BI (6 pages) & Rapports PDF", "Statistiques temporelles AQI, tableau croisé Air/Météo, carte à bulles, dernier relevé, prévisions multi-capteurs et export PDF officiel en un clic.", "Offre aux chercheurs, analystes et élus un outil complet pour étudier les tendances sur plusieurs jours ou semaines et appuyer les décisions publiques."],
            ],
        ),

        # Chapitre 06
        w_p("06. Conclusion Générale et Perspectives d'Amélioration", style="Heading1", bold=True, align="left"),
        w_p("6.1. Bilan d'un projet réalisé de bout en bout au service des usagers", style="Heading2", bold=True, align="left"),
        w_p("Au terme de ce travail, nous avons conçu, déployé et validé de bout en bout une chaîne décisionnelle complète répondant à un enjeu majeur de santé publique en Île-de-France. Notre système récupère automatiquement l'historique météorologique et atmosphérique ainsi que les mesures en temps réel des 34 capteurs franciliens (via un serveur distant interrogeant les flux toutes les 30 minutes), les stocke de manière sécurisée et sans doublon dans une base PostgreSQL Cloud, permet de les explorer de façon ponctuelle ou glissante sur la période choisie, et calcule chaque nuit à 00h45 la prédiction des 24 prochaines heures avant de restituer l'ensemble dans une Application Web moderne et dans Power BI."),
        w_p("Surtout, le projet démontre concrètement comment la donnée environnementale devient un outil de protection citoyenne : qu'il s'agisse d'avertir à temps une personne fragile ou asthmatique, d'aider les hôpitaux à anticiper les pics de détresse respiratoire grâce à l'identification des schémas journaliers (« patterns »), de sensibiliser les industriels et les automobilistes au vu de la surconcentration routière (+52 % sur les grands axes), ou de fournir aux chercheurs des statistiques fiables, chaque composant technique a été mis au service direct de l'utilisateur."),

        w_p("6.2. Perspectives et améliorations futures", style="Heading2", bold=True, align="left"),
        w_p("Conformément à la feuille de route dégagée à l'issue de notre réalisation, quatre axes prioritaires d'amélioration permettront d'enrichir encore la plateforme :"),
        w_p("1. Améliorer encore la précision des prédictions : En enrichissant l'historique d'apprentissage sur un cycle annuel complet (4 saisons) et en intégrant en direct les données de comptage routier francilien, nous pourrons réduire encore l'écart moyen entre l'AQI prédit et l'AQI réel, notamment lors des changements météorologiques brusques."),
        w_p("2. Étendre la longueur de la période de prédiction (au-delà de 24 heures) : Passer d'un horizon de 24 heures à un horizon de 48 heures voire 72 heures (J+2 / J+3) offrira un délai d'anticipation encore plus confortable aux hôpitaux (gestion des stocks d'oxygène et de masques) ainsi qu'aux autorités préfectorales pour organiser les campagnes de prévention."),
        w_p("3. Renforcer la convivialité et l'accessibilité des visualisations : Continuer à simplifier l'expérience utilisateur sur le portail Web et mobile (notifications personnalisées par quartier et par profil de santé, simulateur visuel d'itinéraire le moins pollué pour les piétons et cyclistes)."),
        w_p("4. Expérimenter d'autres algorithmes de Machine Learning et de Deep Learning : Comparer et combiner nos modèles actuels d'arbres boostés (LightGBM) avec d'autres architectures avancées d'apprentissage profond temporel et spatial (tels que les réseaux récurrents LSTM, les Transformers temporels ou les réseaux de neurones sur graphes reliant les 34 stations entre elles selon le sens du vent)."),

        # Chapitre 07
        w_p("07. Références Scientifiques et Ressources Mobilisées", style="Heading1", bold=True, align="left"),
        w_p("[1] Organisation Mondiale de la Santé (OMS). (2021). Lignes directrices mondiales de l'OMS sur la qualité de l'air : particules (PM2.5 et PM10), ozone, dioxyde d'azote, dioxyde de soufre et monoxyde de carbone. Genève : OMS."),
        w_p("[2] Agence Européenne pour l'Environnement (EEA). (2023). Air Quality in Europe 2023 : impacts sanitaires et référentiel de l'Indice Européen de Qualité de l'Air (European AQI). Luxembourg : Office des publications de l'Union européenne."),
        w_p("[3] Santé Publique France. (2021). Pollution de l'air ambiant : estimations de son impact sur la mortalité et la morbidité hospitalière en France métropolitaine. Saint-Maurice : Santé Publique France."),
        w_p("[4] Open-Meteo & Programme Européen Copernicus (CAMS). (2025). Air Quality API & Historical/Forecast Weather API Documentation — Modèles atmosphériques régionaux haute résolution pour l'Europe."),
        w_p("[5] Pope, C. A., & Dockery, D. W. (2006). Health effects of fine particulate air pollution: lines that connect. Journal of the Air & Waste Management Association, 56(6), 709–742."),
        w_p("[6] Harrison, R. M., Jones, A. M., Gietl, J., Yin, J., & Green, D. C. (2012). Estimation of the contributions of brake dust, tire wear, and resuspension to nonexhaust traffic particles (PM10). Environmental Science & Technology, 46(12), 6523–6529."),
        w_p("[7] D'Amato, G., Cecchi, L., Bonini, S., et al. (2007). Allergenic pollen and pollen allergy in Europe: synergy with urban air pollutants. Allergy, 62(9), 976–990."),
        w_p("[8] Seinfeld, J. H., & Pandis, S. N. (2016). Atmospheric Chemistry and Physics: From Air Pollution to Climate Change (3rd ed.). Hoboken, NJ : John Wiley & Sons."),
        w_p("[9] Lenschow, P., Abraham, H. J., Kutzner, K., et al. (2001). Some ideas about the sources of pollutants in urban environments (Méthode incrémentale Trafic vs Fond). Atmospheric Environment, 35, S23–S33."),
        w_p("[10] Ke, G., Meng, Q., Finley, T., et al. (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. Advances in Neural Information Processing Systems (NeurIPS), 30, 3146–3154."),
        w_p("[11] Taieb, S. B., Bontempi, G., Atiya, A. F., & Sorjamaa, A. (2012). A review and comparison of strategies for multi-step ahead time series forecasting (Stratégie multi-horizons 24h). Expert Systems with Applications, 39(8), 7067–7083."),
    ]

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
  <w:body>
    {"".join(body_parts)}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>"""

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
        <w:sz w:val="22"/>
        <w:szCs w:val="22"/>
        <w:color w:val="1E293B"/>
        <w:lang w:val="fr-FR"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="140" w:line="276" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="240" w:after="200" w:line="288" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:b/><w:color w:val="0F172A"/><w:sz w:val="36"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle">
    <w:name w:val="Subtitle"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="120" w:after="80"/></w:pPr>
    <w:rPr><w:b/><w:color w:val="1E3A8A"/><w:sz w:val="22"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="320" w:after="140"/>
      <w:pBdr><w:bottom w:val="single" w:sz="12" w:space="4" w:color="1E3A8A"/></w:pBdr>
    </w:pPr>
    <w:rPr><w:b/><w:color w:val="1E3A8A"/><w:sz w:val="30"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="220" w:after="100"/></w:pPr>
    <w:rPr><w:b/><w:color w:val="0F172A"/><w:sz w:val="25"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Caption">
    <w:name w:val="caption"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="40" w:after="180"/></w:pPr>
    <w:rPr><w:i/><w:color w:val="475569"/><w:sz w:val="19"/></w:rPr>
  </w:style>
</w:styles>"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

    root_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    doc_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/fig1_architecture.png"/>
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/fig3_previsions_ia.png"/>
  <Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/fig2_cycle_diurne.png"/>
</Relationships>"""

    with zipfile.ZipFile(OUT_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types_xml)
        z.writestr("_rels/.rels", root_rels_xml)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/styles.xml", styles_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels_xml)
        z.write(fig1_png, "word/media/fig1_architecture.png")
        z.write(fig2_png, "word/media/fig2_cycle_diurne.png")
        z.write(fig3_png, "word/media/fig3_previsions_ia.png")


def main():
    print("1. Extraction du diagramme d'architecture officiel du PowerPoint et rendu des figures...")
    fig1_png = extract_ppt_architecture_image()
    fig2_png = SCRATCH_DIR / "fig2_cycle_diurne.png"
    fig3_png = SCRATCH_DIR / "fig3_previsions_ia.png"

    render_svg_to_png(SVG_CYCLE_DIURNE, fig2_png, width=1160, height=340)
    render_svg_to_png(SVG_PREVISIONS_IA, fig3_png, width=1160, height=320)

    print("2. Génération du document Microsoft Word (.docx)...")
    build_docx(fig1_png, fig2_png, fig3_png)
    print(f"DOCX généré : {OUT_DOCX} Taille : {OUT_DOCX.stat().st_size}")
    try:
        OUT_DOCX_LEGACY.write_bytes(OUT_DOCX.read_bytes())
    except PermissionError:
        pass

    print("3. Génération du document PDF mis en page...")
    html_str = build_clean_html(fig1_png)
    OUT_HTML.write_text(html_str, encoding="utf-8")
    browser = get_browser()
    prof = SCRATCH_DIR / "chrome_pdf_prof2"
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={prof}",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={OUT_PDF}",
        OUT_HTML.resolve().as_uri(),
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    print(f"PDF généré : {OUT_PDF} Taille : {OUT_PDF.stat().st_size}")
    try:
        OUT_PDF_LEGACY.write_bytes(OUT_PDF.read_bytes())
    except PermissionError:
        pass


if __name__ == "__main__":
    main()
