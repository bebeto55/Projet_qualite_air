import { useState } from 'react';
import { useAirQuality } from '../hooks/useAirQuality';
import PredictionChart from '../components/charts/PredictionChart';
import { getAqiLevel } from '../utils/airQuality';
import { TrendingUp, Info } from 'lucide-react';
import './Predictions.css';

const MODEL_INFO = [
  { label: 'Algorithme', value: 'Random Forest Regressor' },
  { label: 'Variables', value: 'PM2.5 (7j), météo, jour de la semaine, saison' },
  { label: 'Précision (MAPE)', value: '~18%' },
  { label: 'Score R²', value: '0.78' },
  { label: 'Données d\'entraînement', value: '6 mois historique' },
  { label: 'Mise à jour', value: 'Quotidienne à 01h00' },
];

export default function Predictions() {
  const { predictions, loading } = useAirQuality();
  const [showInfo, setShowInfo] = useState(false);

  if (loading) return <div className="loading-screen"><div className="spinner" /></div>;

  const tomorrow = predictions[1];
  const tomorrowLevel = tomorrow ? getAqiLevel(tomorrow.aqi) : null;

  return (
    <div className="predictions-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Prédictions IA</h1>
          <p className="page-subtitle">Prévision PM2.5 à J+7 par modèle Machine Learning</p>
        </div>
        <button className="btn btn-outline" onClick={() => setShowInfo(s => !s)}>
          <Info size={15} /> Infos modèle
        </button>
      </div>

      {/* Model info panel */}
      {showInfo && (
        <div className="card model-info fade-in">
          <h3><TrendingUp size={16} /> Informations sur le modèle prédictif</h3>
          <div className="model-grid">
            {MODEL_INFO.map(m => (
              <div key={m.label} className="model-row">
                <span className="model-key">{m.label}</span>
                <span className="model-val">{m.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tomorrow highlight */}
      {tomorrow && tomorrowLevel && (
        <div className="card tomorrow-card" style={{ borderColor: tomorrowLevel.color, background: `${tomorrowLevel.color}11` }}>
          <div className="tomorrow-header">
            <div>
              <div className="tomorrow-label">Prévision pour demain</div>
              <div className="tomorrow-date">{tomorrow.dateLabel}</div>
            </div>
            <span className={`badge badge-${tomorrowLevel.badge}`} style={{ fontSize: 14 }}>{tomorrowLevel.label}</span>
          </div>
          <div className="tomorrow-values">
            <div className="tomorrow-val">
              <span>PM2.5 prédit</span>
              <strong style={{ color: tomorrowLevel.color, fontSize: 32 }}>{tomorrow.predicted} µg/m³</strong>
            </div>
            <div className="tomorrow-val">
              <span>Intervalle de confiance</span>
              <strong>[{tomorrow.lower} – {tomorrow.upper}] µg/m³</strong>
            </div>
            <div className="tomorrow-val">
              <span>Fiabilité</span>
              <strong style={{ color: tomorrow.confidence > 80 ? 'var(--secondary)' : 'var(--warning)' }}>
                {tomorrow.confidence}%
              </strong>
            </div>
          </div>
          <p className="tomorrow-reco">{tomorrowLevel.recommendation}</p>
        </div>
      )}

      {/* Full prediction chart */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Prévisions sur 7 jours</h2>
          <span className="card-badge">Zone de confiance affichée</span>
        </div>
        <PredictionChart data={predictions} />
      </div>

      {/* Day cards */}
      <div className="pred-day-grid">
        {predictions.map((d, i) => {
          const level = getAqiLevel(d.aqi);
          return (
            <div key={d.date} className="pred-day-card card" style={{ borderColor: i === 1 ? level.color : undefined }}>
              {i === 0 && <div className="pred-today-tag">Aujourd'hui</div>}
              {i === 1 && <div className="pred-today-tag" style={{ background: level.color }}>Demain</div>}
              <div className="pred-day-date">{d.dateLabel}</div>
              <div className="pred-day-pm" style={{ color: level.color }}>{d.predicted}</div>
              <div className="pred-day-unit">µg/m³ PM2.5</div>
              <span className={`badge badge-${level.badge}`} style={{ fontSize: 10 }}>{level.label}</span>
              <div className="pred-day-conf">
                <div className="conf-bar">
                  <div className="conf-fill" style={{
                    width: `${d.confidence}%`,
                    background: d.confidence > 80 ? 'var(--secondary)' : d.confidence > 60 ? 'var(--warning)' : 'var(--danger)'
                  }} />
                </div>
                <span style={{ fontSize: 10 }}>{d.confidence}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
