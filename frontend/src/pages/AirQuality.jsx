import PollutionChart from '../components/charts/PollutionChart';
import { useAirQuality } from '../hooks/useAirQuality';
import { Wind, Filter } from 'lucide-react';
import { useState } from 'react';
import './AirQuality.css';

const POLLUTANT_INFO = [
  { key: 'pm25', name: 'PM2.5', desc: 'Particules fines < 2.5 µm. Pénètrent profondément dans les poumons.', limit: '50 µg/m³', source: 'Trafic, industrie, chauffage' },
  { key: 'pm10', name: 'PM10',  desc: 'Particules < 10 µm. Irritation des voies respiratoires.', limit: '80 µg/m³', source: 'Construction, agriculture, vent' },
  { key: 'no2',  name: 'NO₂',  desc: 'Dioxyde d\'azote. Gaz irritant issu de la combustion.', limit: '200 µg/m³', source: 'Moteurs diesel, chaufferies' },
  { key: 'o3',   name: 'O₃',   desc: 'Ozone. Polluant secondaire formé par réaction photochimique.', limit: '100 µg/m³', source: 'Réaction UV + NOx + COV' },
  { key: 'so2',  name: 'SO₂',  desc: 'Dioxyde de soufre. Irritant pulmonaire.', limit: '350 µg/m³', source: 'Industrie, raffinerie' },
];

export default function AirQuality() {
  const { current, history, loading } = useAirQuality();
  const [filter, setFilter] = useState('all');
  const [hours, setHours]   = useState(24);

  if (loading) return <div className="loading-screen"><div className="spinner" /></div>;

  const data = history.slice(-hours);

  return (
    <div className="air-quality-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Qualité de l'air</h1>
          <p className="page-subtitle">Données détaillées par polluant</p>
        </div>
        <div className="header-actions">
          <select className="select-sm" value={hours} onChange={e => setHours(+e.target.value)}>
            <option value={6}>6h</option>
            <option value={12}>12h</option>
            <option value={24}>24h</option>
            <option value={48}>48h</option>
          </select>
        </div>
      </div>

      {/* Main chart */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Évolution temporelle des polluants</h2>
        </div>
        <PollutionChart data={data} type="area" />
      </div>

      {/* Pollutant detail cards */}
      <div className="pollutant-grid">
        {POLLUTANT_INFO.map(p => {
          const val = current?.[p.key];
          return (
            <div key={p.key} className="pollutant-card card">
              <div className="pollutant-header">
                <div className="pollutant-name">
                  <Wind size={16} />
                  {p.name}
                </div>
                <div className="pollutant-value">{val ?? '—'} <span>µg/m³</span></div>
              </div>
              <div className="pollutant-bar-wrap">
                <div className="pollutant-bar">
                  <div className="pollutant-fill"
                    style={{
                      width: `${Math.min(100, ((val ?? 0) / parseFloat(p.limit)) * 100)}%`,
                      background: (val ?? 0) > parseFloat(p.limit) * 0.8 ? 'var(--danger)' :
                                   (val ?? 0) > parseFloat(p.limit) * 0.5 ? 'var(--warning)' : 'var(--secondary)',
                    }}
                  />
                  <div className="pollutant-limit-marker" style={{ left: '80%' }} title={`Seuil: ${p.limit}`} />
                </div>
                <div className="pollutant-bar-labels">
                  <span>0</span><span>Seuil: {p.limit}</span>
                </div>
              </div>
              <p className="pollutant-desc">{p.desc}</p>
              <div className="pollutant-meta">
                <div><span>Sources</span> {p.source}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
