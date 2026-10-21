import { useState, useEffect } from 'react';
import PowerBIPanel from '../components/powerbi/PowerBIPanel';
import { powerBiService } from '../services/api';
import './PowerBIPage.css';

export default function PowerBIPage() {
  const [embedConfig, setEmbedConfig] = useState(null);
  const [analytics, setAnalytics]     = useState(null);
  const [hours, setHours]             = useState(192);
  const [loading, setLoading]         = useState(true);

  useEffect(() => {
    setLoading(true);
    const envConfig = {
      reportId:    import.meta.env.VITE_POWERBI_REPORT_ID,
      embedUrl:    import.meta.env.VITE_POWERBI_EMBED_URL,
      accessToken: import.meta.env.VITE_POWERBI_ACCESS_TOKEN,
    };
    const hasEnvConfig = Object.values(envConfig).every(Boolean);

    Promise.all([
      powerBiService.getAnalytics(hours).catch(() => null),
      hasEnvConfig ? Promise.resolve(envConfig) : powerBiService.getEmbedConfig().catch(() => null),
    ]).then(([biData, pbiCfg]) => {
      setAnalytics(biData);
      setEmbedConfig(pbiCfg);
      setLoading(false);
    });
  }, [hours]);

  return (
    <div className="powerbi-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Power BI & Business Intelligence</h1>
          <p className="page-subtitle">
            Analyse multidimensionnelle en direct sur Supabase ({analytics?.totalRows ?? '—'} mesures · 34 stations Île-de-France)
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <select className="select-sm" value={hours} onChange={e => setHours(+e.target.value)}>
            <option value={48}>48 dernières heures</option>
            <option value={168}>7 derniers jours (168h)</option>
            <option value={192}>8 derniers jours (192h)</option>
            <option value={360}>15 derniers jours</option>
          </select>
          <a
            href={`http://localhost:8080/api/powerbi/dataset.csv?hours=${hours}`}
            className="btn btn-outline"
            download={`smart_city_supabase_${hours}h.csv`}
          >
            ⬇ Dataset Power BI (.CSV)
          </a>
          <div className="pbi-badge">
            <span className="pbi-dot" />
            Supabase Live BI
          </div>
        </div>
      </div>

      {loading
        ? <div className="loading-screen"><div className="spinner" /></div>
        : <PowerBIPanel embedConfig={embedConfig} analytics={analytics} />
      }
    </div>
  );
}
