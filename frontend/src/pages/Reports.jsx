import { useState } from 'react';
import { FileText, Download, Calendar, Loader } from 'lucide-react';
import { useAirQuality } from '../hooks/useAirQuality';
import { getAqiLevel, formatDateTime } from '../utils/airQuality';
import toast from 'react-hot-toast';
import './Reports.css';

const REPORT_TYPES = [
  { id: 'weekly',  label: 'Rapport hebdomadaire', desc: 'Synthèse des 7 derniers jours (168h)', hours: 168 },
  { id: 'daily',   label: 'Rapport journalier',   desc: 'Analyse des dernières 24 heures',      hours: 24 },
  { id: 'alert',   label: 'Rapport d\'alerte',    desc: 'Épisodes de pollution & anomalies',    hours: 48 },
  { id: 'sensors', label: 'État du parc IoT',     desc: 'Bilan des 34 stations Île-de-France',  hours: 24 },
];

export default function Reports() {
  const { current, history, sensors, alerts } = useAirQuality(60_000, 168);
  const [selected, setSelected]     = useState('weekly');
  const [dateFrom, setDateFrom]     = useState('');
  const [dateTo, setDateTo]         = useState('');
  const [generating, setGenerating] = useState(false);
  const [format, setFormat]         = useState('pdf');
  const [generatedHistory, setGeneratedHistory] = useState([]);

  const downloadBlob = (content, filename, mime) => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const generate = async () => {
    setGenerating(true);
    try {
      const reportType = REPORT_TYPES.find(t => t.id === selected) || REPORT_TYPES[0];
      const nowStr = new Date().toISOString().slice(0, 10);
      const filteredHistory = history.slice(-reportType.hours);

      if (format === 'csv' || format === 'xlsx') {
        const rows = [
          ['Horodatage', 'EAQI', 'PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'NO2 (µg/m³)', 'O3 (µg/m³)', 'SO2 (µg/m³)', 'Temp (°C)', 'Humidité (%)', 'Vent (km/h)'],
          ...filteredHistory.map(r => [
            r.time, r.aqi ?? '', r.pm25 ?? '', r.pm10 ?? '', r.no2 ?? '', r.o3 ?? '', r.so2 ?? '', r.temp ?? '', r.humidity ?? '', r.wind ?? '',
          ]),
        ];
        const csv = '\uFEFF' + rows.map(r => r.join(';')).join('\n');
        const fname = `rapport-${selected}-${nowStr}.csv`;
        downloadBlob(csv, fname, 'text/csv;charset=utf-8;');
        setGeneratedHistory(h => [{ id: Date.now(), name: `${reportType.label} (${nowStr})`, date: nowStr, size: `${(csv.length / 1024).toFixed(1)} KB`, type: selected }, ...h]);
        toast.success('Export CSV généré et téléchargé !');
      } else {
        const level = current ? getAqiLevel(current.aqi) : null;
        const html = `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>${reportType.label} — Smart City Île-de-France</title>
        <style>body{font-family:Segoe UI,Arial,sans-serif;margin:32px;color:#0f172a}h1{margin-bottom:4px}table{width:100%;border-collapse:collapse;margin-top:16px;font-size:12px}th,td{border:1px solid #cbd5e1;padding:6px 8px;text-align:left}th{background:#f1f5f9}.kpi{display:inline-block;border:1px solid #cbd5e1;border-radius:8px;padding:10px 16px;margin:6px 8px 6px 0}</style></head><body>
        <h1>${reportType.label} — Qualité de l'Air Île-de-France</h1>
        <p>Généré le ${formatDateTime(new Date())} · Stations actives : ${sensors.filter(s => s.status === 'online').length}/${sensors.length}</p>
        ${current ? `<div>
          <div class="kpi"><strong>Indice EAQI moyen :</strong> ${current.aqi} (${level?.label || ''})</div>
          <div class="kpi"><strong>PM2.5 :</strong> ${current.pm25} µg/m³</div>
          <div class="kpi"><strong>PM10 :</strong> ${current.pm10} µg/m³</div>
          <div class="kpi"><strong>NO₂ :</strong> ${current.no2} µg/m³</div>
          <div class="kpi"><strong>O₃ :</strong> ${current.o3} µg/m³</div>
        </div>` : ''}
        <h2>Alertes & Anomalies actives (${alerts.length})</h2>
        ${alerts.length ? `<table><thead><tr><th>Station</th><th>Polluant</th><th>Valeur</th><th>Détail</th></tr></thead><tbody>
          ${alerts.map(a => `<tr><td>${a.sensor}</td><td>${a.pollutant}</td><td>${a.value} µg/m³</td><td>${a.type === 'anomaly' ? `Z-score ${a.zScore}` : `Seuil ${a.threshold} µg/m³`}</td></tr>`).join('')}
        </tbody></table>` : '<p>Aucune alerte active.</p>'}
        <h2>État des 34 stations de mesure</h2>
        <table><thead><tr><th>Station</th><th>EAQI</th><th>PM2.5</th><th>PM10</th><th>NO₂</th><th>O₃</th><th>Temp</th><th>Statut</th></tr></thead><tbody>
          ${sensors.map(s => `<tr><td>${s.name}</td><td>${s.aqi ?? '—'}</td><td>${s.pm25 ?? '—'}</td><td>${s.pm10 ?? '—'}</td><td>${s.no2 ?? '—'}</td><td>${s.o3 ?? '—'}</td><td>${s.temp ?? '—'} °C</td><td>${s.status}</td></tr>`).join('')}
        </tbody></table>
        <script>window.onload = () => window.print();</script>
        </body></html>`;
        const win = window.open('', '_blank');
        if (win) {
          win.document.write(html);
          win.document.close();
        } else {
          downloadBlob(html, `rapport-${selected}-${nowStr}.html`, 'text/html;charset=utf-8;');
        }
        setGeneratedHistory(h => [{ id: Date.now(), name: `${reportType.label} (${nowStr})`, date: nowStr, size: `${(html.length / 1024).toFixed(1)} KB`, type: selected }, ...h]);
        toast.success('Rapport prêt pour impression / enregistrement PDF !');
      }
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="reports-page fade-in">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">Rapports</h1>
          <p className="page-subtitle">Génération de rapports PDF & CSV à partir des données réelles d'Île-de-France</p>
        </div>
        <a
          href="http://localhost:8080/api/reports/project-pdf"
          download="Rapport_Projet_Smart_City.pdf"
          className="btn btn-primary"
          style={{ textDecoration: 'none' }}
        >
          <Download size={15} /> Télécharger le Dossier Complet du Projet (PDF Illustré)
        </a>
      </div>

      <div className="reports-grid">
        {/* Generator */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><FileText size={15} /> Générer un rapport</h2>
          </div>

          <div className="report-form">
            <div className="form-group">
              <label>Type de rapport</label>
              <div className="report-type-grid">
                {REPORT_TYPES.map(t => (
                  <button
                    key={t.id}
                    className={`report-type-btn ${selected === t.id ? 'selected' : ''}`}
                    onClick={() => setSelected(t.id)}
                  >
                    <strong>{t.label}</strong>
                    <span>{t.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label><Calendar size={13} /> Du</label>
                <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} className="date-input" />
              </div>
              <div className="form-group">
                <label><Calendar size={13} /> Au</label>
                <input type="date" value={dateTo}   onChange={e => setDateTo(e.target.value)}   className="date-input" />
              </div>
            </div>

            <div className="form-group">
              <label>Format de sortie</label>
              <div className="format-selector">
                {['pdf', 'csv'].map(f => (
                  <button key={f} className={`format-btn ${format === f ? 'selected' : ''}`} onClick={() => setFormat(f)}>
                    {f.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <button className="btn btn-primary generate-btn" onClick={generate} disabled={generating}>
              {generating
                ? <><Loader size={15} className="spinning" /> Génération en cours…</>
                : <><Download size={15} /> Générer le rapport</>}
            </button>
          </div>
        </div>

        {/* History */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Rapports générés durant la session</h2>
          </div>
          <div className="report-history">
            {generatedHistory.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Aucun rapport généré pour le moment.</p>
            ) : generatedHistory.map(r => (
              <div key={r.id} className="report-item">
                <div className="report-item-icon"><FileText size={20} /></div>
                <div className="report-item-info">
                  <strong>{r.name}</strong>
                  <span>{r.date} · {r.size}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
