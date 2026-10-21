import { useState, useEffect } from 'react';
import PowerBIPanel from '../components/powerbi/PowerBIPanel';
import { powerBiService } from '../services/api';
import './PowerBIPage.css';

export default function PowerBIPage() {
  const [embedConfig, setEmbedConfig] = useState(null);
  const [loading, setLoading]         = useState(true);

  useEffect(() => {
    // Try fetching embed config from backend; fall back to env vars
    const envConfig = {
      reportId:    import.meta.env.VITE_POWERBI_REPORT_ID,
      embedUrl:    import.meta.env.VITE_POWERBI_EMBED_URL,
      accessToken: import.meta.env.VITE_POWERBI_ACCESS_TOKEN,
    };

    const hasEnvConfig = Object.values(envConfig).every(Boolean);

    if (hasEnvConfig) {
      setEmbedConfig(envConfig);
      setLoading(false);
    } else {
      powerBiService.getEmbedConfig()
        .then(setEmbedConfig)
        .catch(() => setEmbedConfig(null))
        .finally(() => setLoading(false));
    }
  }, []);

  return (
    <div className="powerbi-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Power BI</h1>
          <p className="page-subtitle">Rapports analytiques avancés et tableaux de bord interactifs</p>
        </div>
        <div className="pbi-badge">
          <span className="pbi-dot" />
          Powered by Microsoft Power BI
        </div>
      </div>

      {loading
        ? <div className="loading-screen"><div className="spinner" /></div>
        : <PowerBIPanel embedConfig={embedConfig} />
      }

      {/* Contextual info */}
      <div className="pbi-info-grid">
        <div className="card pbi-info-card">
          <div className="pbi-info-icon">📈</div>
          <h3>Analyse historique</h3>
          <p>Visualisez l'évolution pluriannuelle des polluants avec filtres dynamiques</p>
        </div>
        <div className="card pbi-info-card">
          <div className="pbi-info-icon">🗺️</div>
          <h3>Cartographie avancée</h3>
          <p>Cartes de chaleur par zone géographique avec corrélations météo</p>
        </div>
        <div className="card pbi-info-card">
          <div className="pbi-info-icon">📊</div>
          <h3>Indicateurs KPI</h3>
          <p>Tableaux de bord personnalisés pour les élus et responsables</p>
        </div>
      </div>
    </div>
  );
}
