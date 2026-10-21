import { useState } from 'react';
import { Wind, Thermometer, Droplets, CloudRain, Activity, MapPin, Clock, AlertTriangle, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAirQuality, useWeather, computeTrend } from '../hooks/useAirQuality';
import { getAqiLevel, formatDateTime, getPollutantStatus } from '../utils/airQuality';
import KpiCard from '../components/dashboard/KpiCard';
import AqiGauge from '../components/dashboard/AqiGauge';
import PollutionChart from '../components/charts/PollutionChart';
import WeatherCorrelationChart from '../components/charts/WeatherCorrelationChart';
import AlertPanel from '../components/alerts/AlertPanel';
import './Dashboard.css';

const STATUS_LABEL = { good: 'Bon', moderate: 'Modéré', 'unhealthy-sg': 'Attention', unhealthy: 'Mauvais', 'very-unhealthy': 'Très mauvais' };

export default function Dashboard() {
  const { current, history, sensors, alerts, loading, error, refresh, acknowledgeAlert } = useAirQuality();
  const { weather } = useWeather();
  const [chartType, setChartType] = useState('area');
  const [timeRange, setTimeRange] = useState(24);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <p>Chargement des données en temps réel…</p>
      </div>
    );
  }

  if (error && !current) {
    return (
      <div className="loading-screen">
        <AlertTriangle size={40} color="var(--danger)" />
        <p>Impossible de charger les données : {error}</p>
        <button className="btn btn-primary" onClick={refresh}><RefreshCw size={14} /> Réessayer</button>
      </div>
    );
  }

  const aqiLevel  = current ? getAqiLevel(current.aqi) : null;
  const last24h   = history.slice(-timeRange);
  const onAck = (id) => acknowledgeAlert(id).then(() => toast.success('Alerte acquittée')).catch(e => toast.error(e.message));
  const pollutantBadge = (key, v) => { const s = getPollutantStatus(key, v); return { type: s, label: STATUS_LABEL[s] || s }; };

  return (
    <div className="dashboard fade-in">
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Tableau de bord</h1>
          <p className="page-subtitle">
            <MapPin size={13} /> Île-de-France · {sensors.length} stations &nbsp;·&nbsp;
            <Clock size={13} /> {current ? formatDateTime(current.updatedAt) : '—'}
          </p>
        </div>
        <div className="header-actions">
          <select className="select-sm" value={timeRange} onChange={e => setTimeRange(+e.target.value)}>
            <option value={6}>6 heures</option>
            <option value={12}>12 heures</option>
            <option value={24}>24 heures</option>
            <option value={48}>48 heures</option>
          </select>
          <select className="select-sm" value={chartType} onChange={e => setChartType(e.target.value)}>
            <option value="area">Graphique en surface</option>
            <option value="line">Graphique en ligne</option>
          </select>
        </div>
      </div>

      {/* AQI banner */}
      {aqiLevel && (
        <div className="aqi-banner card" style={{ borderColor: aqiLevel.color, background: `${aqiLevel.color}11` }}>
          <AqiGauge aqi={current.aqi} size={180} />
          <div className="aqi-banner-info">
            <div className="aqi-banner-label">
              <span className={`badge badge-${aqiLevel.badge}`} style={{ fontSize: 13, padding: '4px 14px' }}>{aqiLevel.label}</span>
            </div>
            <p className="aqi-recommendation">{aqiLevel.recommendation}</p>
            <div className="aqi-meta">
              <span>Station : <strong>{current.station}</strong></span>
              <span>Capteurs actifs : <strong>{sensors.filter(s => s.status === 'online').length}/{sensors.length}</strong></span>
            </div>
          </div>
        </div>
      )}

      {/* KPI Grid */}
      <div className="kpi-grid">
        {current && (<>
          <KpiCard
            title="PM2.5" value={current.pm25} unit="µg/m³"
            icon={Wind} color={current.pm25 > 35 ? 'var(--danger)' : 'var(--secondary)'}
            badge={pollutantBadge('pm25', current.pm25)}
            trend={computeTrend(history, 'pm25')}
          />
          <KpiCard
            title="PM10" value={current.pm10} unit="µg/m³"
            icon={Wind} color="var(--warning)"
            badge={pollutantBadge('pm10', current.pm10)}
            trend={computeTrend(history, 'pm10')}
          />
          <KpiCard
            title="NO₂" value={current.no2} unit="µg/m³"
            icon={Activity} color="var(--primary)"
            trend={computeTrend(history, 'no2')}
          />
          <KpiCard
            title="O₃" value={current.o3} unit="µg/m³"
            icon={Activity} color="#a855f7"
            trend={computeTrend(history, 'o3')}
          />
          {weather && (<>
            <KpiCard
              title="Température" value={weather.temp} unit="°C"
              icon={Thermometer} color="#f59e0b"
              trend={computeTrend(history, 'temp')}
            />
            <KpiCard
              title="Humidité" value={weather.humidity} unit="%"
              icon={Droplets} color="#0ea5e9"
              subValue={`Vent ${weather.wind} km/h ${weather.windDir}`}
            />
            <KpiCard
              title="Précipitations" value={weather.precipitation} unit="mm"
              icon={CloudRain} color="#8b5cf6"
              subValue={weather.description}
            />
          </>)}
        </>)}
      </div>

      {/* Charts row */}
      <div className="charts-grid">
        <div className="card chart-card">
          <div className="card-header">
            <h2 className="card-title">Évolution des polluants — {timeRange}h</h2>
          </div>
          <PollutionChart data={last24h} type={chartType} />
        </div>

        <div className="card chart-card">
          <div className="card-header">
            <h2 className="card-title">Corrélation Pollution / Météo</h2>
          </div>
          <WeatherCorrelationChart data={last24h} />
        </div>
      </div>

      {/* Sensors + Alerts row */}
      <div className="bottom-grid">
        {/* Sensor table */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Capteurs IoT</h2>
            <span className="card-badge">{sensors.filter(s => s.status === 'online').length} en ligne</span>
          </div>
          <div className="sensor-table-wrap">
            <table className="sensor-table">
              <thead>
                <tr>
                  <th>Capteur</th><th>PM2.5</th><th>PM10</th><th>NO₂</th><th>Temp</th><th>Statut</th>
                </tr>
              </thead>
              <tbody>
                {sensors.map(s => (
                  <tr key={s.id}>
                    <td><strong>{s.name}</strong></td>
                    <td style={{ color: s.pm25 > 35 ? 'var(--danger)' : 'var(--secondary)' }}>{s.pm25}</td>
                    <td>{s.pm10}</td>
                    <td>{s.no2}</td>
                    <td>{s.temp}°C</td>
                    <td>
                      <span className={`status-pill ${s.status}`}>
                        <span className="status-dot" />
                        {s.status === 'online' ? 'En ligne' : 'Hors ligne'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Alerts */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Alertes actives</h2>
            {alerts.length > 0 && <span className="card-badge danger">{alerts.length}</span>}
          </div>
          <AlertPanel alerts={alerts} onAcknowledge={onAck} />
        </div>
      </div>
    </div>
  );
}
