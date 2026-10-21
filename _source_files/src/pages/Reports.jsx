import { useState } from 'react';
import { FileText, Download, Calendar, Loader } from 'lucide-react';
import toast from 'react-hot-toast';
import './Reports.css';

const REPORT_TYPES = [
  { id: 'weekly',  label: 'Rapport hebdomadaire', desc: 'Synthèse des 7 derniers jours' },
  { id: 'monthly', label: 'Rapport mensuel',      desc: 'Analyse du mois écoulé' },
  { id: 'alert',   label: 'Rapport d\'alerte',    desc: 'Épisodes de pollution > seuil' },
  { id: 'trend',   label: 'Analyse de tendances', desc: 'Évolution sur 30 jours' },
];

const HISTORY = [
  { id: 1, name: 'Rapport hebdo – S39 2025', date: '2025-09-28', size: '2.3 MB', type: 'weekly' },
  { id: 2, name: 'Rapport mensuel – Août 2025', date: '2025-09-01', size: '5.1 MB', type: 'monthly' },
  { id: 3, name: 'Alerte pollution – 22 août', date: '2025-08-22', size: '0.8 MB', type: 'alert' },
];

export default function Reports() {
  const [selected, setSelected]     = useState('weekly');
  const [dateFrom, setDateFrom]     = useState('');
  const [dateTo, setDateTo]         = useState('');
  const [generating, setGenerating] = useState(false);
  const [format, setFormat]         = useState('pdf');

  const generate = async () => {
    setGenerating(true);
    // Simulate generation delay
    await new Promise(r => setTimeout(r, 2500));
    setGenerating(false);
    toast.success('Rapport généré et téléchargé !');
    // In production: call reportService.generate({ type: selected, dateFrom, dateTo, format })
    // then URL.createObjectURL(blob) + download link
  };

  return (
    <div className="reports-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Rapports</h1>
          <p className="page-subtitle">Génération de rapports PDF pour les élus et les services</p>
        </div>
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
                {['pdf', 'xlsx', 'csv'].map(f => (
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
            <h2 className="card-title">Historique des rapports</h2>
          </div>
          <div className="report-history">
            {HISTORY.map(r => (
              <div key={r.id} className="report-item">
                <div className="report-item-icon"><FileText size={20} /></div>
                <div className="report-item-info">
                  <strong>{r.name}</strong>
                  <span>{r.date} · {r.size}</span>
                </div>
                <button className="icon-btn" title="Télécharger" onClick={() => toast.success(`Téléchargement de ${r.name}`)}>
                  <Download size={15} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
