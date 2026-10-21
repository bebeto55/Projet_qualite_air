import { Car, Bus, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useAirQuality, computeTrend } from '../hooks/useAirQuality';
import './Mobility.css';

// Capteurs situés directement sur des axes routiers majeurs en Île-de-France
const ROAD_SENSOR_IDS = new Set([
  '203098',    // Autoroute A1 Saint-denis
  '283088',    // Boulevard Peripherique Est
  '23095',     // Route Nationale 6 - Melun
  '3314715',   // Rn20 Montlhery
  '243086',    // Champs Elysees
  '193092',    // Place De Lopera Paris
  '143091',    // Place Victor Basch
  '5-2218252', // Boulevard de Denain
]);

export default function Mobility() {
  const { history, sensors, loading } = useAirQuality(60_000, 24);

  if (loading) return <div className="loading-screen"><div className="spinner" /></div>;

  const roadSensors = sensors.filter(s => ROAD_SENSOR_IDS.has(String(s.id)) && s.no2 != null);
  const bgSensors   = sensors.filter(s => !ROAD_SENSOR_IDS.has(String(s.id)) && s.no2 != null);

  const avgRoadNo2 = roadSensors.length
    ? roadSensors.reduce((sum, s) => sum + s.no2, 0) / roadSensors.length
    : 20;
  const avgBgNo2 = bgSensors.length
    ? bgSensors.reduce((sum, s) => sum + s.no2, 0) / bgSensors.length
    : 12;

  // Indice de pression routière dérivé du NO2 sur les grands axes (0-100%)
  const trafficIndex = Math.min(100, Math.round((avgRoadNo2 / 50) * 100));
  const roadOverBgPct = avgBgNo2 > 0 ? Math.round(((avgRoadNo2 - avgBgNo2) / avgBgNo2) * 100) : 0;
  const no2Trend = computeTrend(history, 'no2', 12) ?? 0;

  // Courbe horaire réelle sur les 24 dernières heures
  const chartData = history.slice(-24).map(h => {
    const hour = new Date(h.time).getHours();
    const isPeak = (hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19);
    const no2Val = h.no2 ?? 0;
    return {
      time: h.timeLabel,
      no2Trafic: +(no2Val).toFixed(1),
      pm10Route: +(h.pm10 ?? 0).toFixed(1),
      pm25: +(h.pm25 ?? 0).toFixed(1),
      pressionHoraire: Math.min(100, Math.round((no2Val / 45) * 100 + (isPeak ? 15 : 0))),
    };
  });

  // Axes les plus chargés en NO2 actuellement
  const topRoadSensors = [...roadSensors].sort((a, b) => (b.no2 ?? 0) - (a.no2 ?? 0));

  return (
    <div className="mobility-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Mobilité et Axes Routiers</h1>
          <p className="page-subtitle">
            Impact réel du trafic sur la qualité de l'air — {roadSensors.length} stations routières Île-de-France (A1, Périphérique, RN6, RN20, Paris)
          </p>
        </div>
      </div>

      <div className="mobility-kpi-grid">
        <div className="card mobility-kpi">
          <div className="mobility-kpi-icon" style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', color: 'var(--danger)' }}>
            <Car size={24} />
          </div>
          <div className="mobility-kpi-content">
            <span className="mobility-kpi-label">NO₂ moyen — Axes Routiers</span>
            <div className="mobility-kpi-val">
              <strong>{avgRoadNo2.toFixed(1)} µg/m³</strong>
              <span className={no2Trend >= 0 ? 'trend-up' : 'trend-down'}>
                {no2Trend >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />} {no2Trend >= 0 ? `+${no2Trend}%` : `${no2Trend}%`}
              </span>
            </div>
          </div>
        </div>

        <div className="card mobility-kpi">
          <div className="mobility-kpi-icon" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: 'var(--secondary)' }}>
            <Bus size={24} />
          </div>
          <div className="mobility-kpi-content">
            <span className="mobility-kpi-label">Surconcentration Trafic vs Fond</span>
            <div className="mobility-kpi-val">
              <strong>{roadOverBgPct >= 0 ? `+${roadOverBgPct}%` : `${roadOverBgPct}%`}</strong>
              <span className="trend-flat">Fond : {avgBgNo2.toFixed(1)} µg/m³</span>
            </div>
          </div>
        </div>

        <div className="card mobility-kpi">
          <div className="mobility-kpi-icon" style={{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
            <AlertTriangle size={24} />
          </div>
          <div className="mobility-kpi-content">
            <span className="mobility-kpi-label">Indice d'Émission Trafic</span>
            <div className="mobility-kpi-val">
              <strong>{trafficIndex}%</strong>
              <span className="trend-flat">Max : {topRoadSensors[0]?.name || '—'}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Corrélation Traceurs Trafic (NO₂ / PM10) & Particules Fines PM2.5 (24h réelles)</h2>
        </div>
        <div className="mobility-chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <ComposedChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="time" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <YAxis yAxisId="left" tick={{ fill: 'var(--text-muted)' }} label={{ value: 'µg/m³ (NO₂ / PM10)', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fill: 'var(--text-muted)' }} label={{ value: 'PM2.5 (µg/m³)', angle: 90, position: 'insideRight', fill: 'var(--text-muted)' }} />
              <Tooltip
                contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)', borderRadius: '8px' }}
                itemStyle={{ fontSize: '13px' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar yAxisId="left" dataKey="no2Trafic" name="NO₂ (traceur trafic routier)" fill="var(--danger)" opacity={0.85} radius={[4, 4, 0, 0]} barSize={18} />
              <Bar yAxisId="left" dataKey="pm10Route" name="PM10 (abrasion / remise en suspension)" fill="var(--secondary)" opacity={0.75} radius={[4, 4, 0, 0]} barSize={18} />
              <Line yAxisId="right" type="monotone" dataKey="pm25" name="PM2.5 (µg/m³)" stroke="#a855f7" strokeWidth={3} dot={{ r: 3, fill: '#a855f7' }} activeDot={{ r: 6 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Relevés en direct sur les grands axes routiers d'Île-de-France</h2>
        </div>
        <div className="sensor-table-wrap">
          <table className="sensor-table">
            <thead>
              <tr>
                <th>Axe / Station</th>
                <th>EAQI</th>
                <th>NO₂ (Trafic)</th>
                <th>PM2.5</th>
                <th>PM10</th>
                <th>Vent</th>
              </tr>
            </thead>
            <tbody>
              {topRoadSensors.map(s => (
                <tr key={s.id}>
                  <td><strong>{s.name}</strong></td>
                  <td>{s.aqi}</td>
                  <td style={{ color: s.no2 > 40 ? 'var(--danger)' : 'var(--primary)', fontWeight: 600 }}>{s.no2} µg/m³</td>
                  <td>{s.pm25} µg/m³</td>
                  <td>{s.pm10} µg/m³</td>
                  <td>{s.wind} km/h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
