import { useState } from 'react';
import { usePredictions } from '../hooks/useAirQuality';
import { useAuth } from '../context/AuthContext';
import PredictionChart from '../components/charts/PredictionChart';
import { getAqiLevel, formatDateTime } from '../utils/airQuality';
import { TrendingUp, Info, RefreshCw, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import './Predictions.css';

export default function Predictions() {
  const { data, predictions, loading, error, reload } = usePredictions();
  const { isAdmin } = useAuth();
  const [showInfo, setShowInfo] = useState(false);
  const [sensorId, setSensorId] = useState('');

  if (loading && !data) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <p>Calcul des prévisions par le modèle IA… (jusqu'à 30 s au premier lancement)</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="loading-screen">
        <AlertTriangle size={40} color="var(--danger)" />
        <p>Prévisions indisponibles : {error}</p>
        <button className="btn btn-primary" onClick={() => reload()}><RefreshCw size={14} /> Réessayer</button>
      </div>
    );
  }

  const model = data.model;
  const sensorEntries = Object.entries(data.sensors).sort((a, b) => a[1].name.localeCompare(b[1].name));

  // Series to display: city average (with confidence band) or one station
  const series = sensorId
    ? data.sensors[sensorId].series.map((s, i) => ({ ...predictions[i], ...s, lower: undefined, upper: undefined, aqi: Math.round(s.predicted) }))
    : predictions;

  const peak = series.reduce((m, p) => (p.predicted > (m?.predicted ?? -1) ? p : m), null);
  const peakLevel = peak ? getAqiLevel(peak.predicted) : null;
  const meanPred = series.length ? +(series.reduce((s, p) => s + p.predicted, 0) / series.length).toFixed(1) : null;
  const avgConfidence = predictions.length ? Math.round(predictions.reduce((s, p) => s + p.confidence, 0) / predictions.length) : null;

  const MODEL_INFO = [
    { label: 'Algorithme', value: `${model.name} — ${model.horizons} modèles (un par horizon 1 h → 24 h)` },
    { label: 'Cible', value: 'Indice européen de qualité de l\'air (EAQI)' },
    { label: 'Variables', value: `${model.features} features : polluants passés (lags 1 h → 7 j), météo passée et prévue (Open-Meteo), heure, jour, mois` },
    { label: 'Erreur moyenne (MAE)', value: model.mae != null ? `${model.mae} points EAQI` : '—' },
    { label: 'MAPE back-test', value: model.mape != null ? `${model.mape} %` : '—' },
    { label: 'Fiabilité globale', value: model.reliability != null ? `${model.reliability} %` : '—' },
    { label: 'Back-test', value: `${model.backtestSamples} prévisions comparées aux mesures réelles des dernières 24 h` },
    { label: 'Calculé le', value: `${formatDateTime(data.generatedAt)} (${data.computeSeconds}s)` },
  ];

  const handleRefresh = async () => {
    await reload(true);
    toast.success('Prévisions recalculées');
  };

  return (
    <div className="predictions-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Prédictions IA</h1>
          <p className="page-subtitle">Prévision de l'indice de qualité de l'air sur les 24 prochaines heures (J+1)</p>
        </div>
        <div className="header-actions" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <select className="select-sm" value={sensorId} onChange={e => setSensorId(e.target.value)}>
            <option value="">Moyenne Île-de-France</option>
            {sensorEntries.map(([id, s]) => <option key={id} value={id}>{s.name}</option>)}
          </select>
          <button className="btn btn-outline" onClick={() => setShowInfo(s => !s)}>
            <Info size={15} /> Infos modèle
          </button>
          {isAdmin && (
            <button className="btn btn-outline" onClick={handleRefresh} disabled={loading}>
              <RefreshCw size={15} className={loading ? 'spin' : ''} /> Recalculer
            </button>
          )}
        </div>
      </div>

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

      {peak && peakLevel && (
        <div className="card tomorrow-card" style={{ borderColor: peakLevel.color, background: `${peakLevel.color}11` }}>
          <div className="tomorrow-header">
            <div>
              <div className="tomorrow-label">Prévision 24 h — {sensorId ? data.sensors[sensorId].name : 'Île-de-France'}</div>
              <div className="tomorrow-date">Pic attendu : {peak.dateLabel}</div>
            </div>
            <span className={`badge badge-${peakLevel.badge}`} style={{ fontSize: 14 }}>{peakLevel.label}</span>
          </div>
          <div className="tomorrow-values">
            <div className="tomorrow-val">
              <span>Indice max prévu</span>
              <strong style={{ color: peakLevel.color, fontSize: 32 }}>{peak.predicted}</strong>
            </div>
            <div className="tomorrow-val">
              <span>Moyenne 24 h</span>
              <strong>{meanPred}</strong>
            </div>
            {peak.lower != null && (
              <div className="tomorrow-val">
                <span>Intervalle de confiance (80 %)</span>
                <strong>[{peak.lower} – {peak.upper}]</strong>
              </div>
            )}
            <div className="tomorrow-val">
              <span>Fiabilité moyenne</span>
              <strong style={{ color: avgConfidence > 80 ? 'var(--secondary)' : 'var(--warning)' }}>{avgConfidence}%</strong>
            </div>
          </div>
          <p className="tomorrow-reco">{peakLevel.recommendation}</p>
          {!sensorId && data.summary.worstSensor && (
            <p className="tomorrow-reco">
              Station la plus exposée : <strong>{data.summary.worstSensor.name}</strong> (indice max {data.summary.worstSensor.max24h})
            </p>
          )}
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Évolution heure par heure</h2>
          <span className="card-badge">{sensorId ? 'Station sélectionnée' : 'Zone de confiance 80 % affichée'}</span>
        </div>
        <PredictionChart data={series} />
      </div>

      <div className="pred-day-grid">
        {series.filter((_, i) => i % 3 === 2).map(d => {
          const level = getAqiLevel(d.predicted);
          return (
            <div key={d.date} className="pred-day-card card">
              <div className="pred-day-date">{d.dateLabel}</div>
              <div className="pred-day-pm" style={{ color: level.color }}>{d.predicted}</div>
              <div className="pred-day-unit">indice EAQI · +{d.h}h</div>
              <span className={`badge badge-${level.badge}`} style={{ fontSize: 10 }}>{level.label}</span>
              {d.confidence != null && (
                <div className="pred-day-conf">
                  <div className="conf-bar">
                    <div className="conf-fill" style={{
                      width: `${d.confidence}%`,
                      background: d.confidence > 80 ? 'var(--secondary)' : d.confidence > 60 ? 'var(--warning)' : 'var(--danger)'
                    }} />
                  </div>
                  <span style={{ fontSize: 10 }}>{d.confidence}%</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
