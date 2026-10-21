import { useAirQuality } from '../hooks/useAirQuality';
import AirQualityMap from '../components/map/AirQualityMap';
import { useEffect, useState } from 'react';
import './MapPage.css';

export default function MapPage() {
  const { sensors, loading } = useAirQuality();
  const [selected, setSelected] = useState(null);

  return (
    <div className="map-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Carte interactive</h1>
          <p className="page-subtitle">Distribution spatiale de la qualité de l'air — Marseille Métropole</p>
        </div>
      </div>

      <div className="map-layout">
        <div className="map-main">
          {loading
            ? <div className="loading-screen"><div className="spinner" /></div>
            : <AirQualityMap sensors={sensors} />}
        </div>

        <div className="map-sidebar-panel">
          <h3 className="panel-title">Capteurs ({sensors.length})</h3>
          {sensors.map(s => (
            <div key={s.id} className="sensor-card card">
              <div className="sensor-card-header">
                <strong>{s.name}</strong>
                <span className={`status-pill ${s.status}`}>
                  <span className="status-dot" /> {s.status === 'online' ? 'En ligne' : 'Hors ligne'}
                </span>
              </div>
              <div className="sensor-card-grid">
                <div className="sc-item"><span>PM2.5</span><strong>{s.pm25} µg/m³</strong></div>
                <div className="sc-item"><span>PM10</span><strong>{s.pm10} µg/m³</strong></div>
                <div className="sc-item"><span>NO₂</span><strong>{s.no2} µg/m³</strong></div>
                <div className="sc-item"><span>Temp</span><strong>{s.temp}°C</strong></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
