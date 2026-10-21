import { useState, useEffect } from 'react';
import { Car, Bus, Train, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Mobility.css';

// Simulation data for Mobility
const generateTrafficData = () => {
  const data = [];
  for (let i = 8; i <= 20; i += 2) {
    const isRushHour = i === 8 || i === 18;
    data.push({
      time: `${i}:00`,
      congestion: isRushHour ? 85 + Math.random() * 10 : 40 + Math.random() * 20,
      transportUsage: isRushHour ? 90 + Math.random() * 10 : 30 + Math.random() * 30,
      pollutionImpact: isRushHour ? 70 + Math.random() * 15 : 25 + Math.random() * 20,
    });
  }
  return data;
};

export default function Mobility() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API fetch
    setTimeout(() => {
      setData(generateTrafficData());
      setLoading(false);
    }, 800);
  }, []);

  if (loading) return <div className="loading-screen"><div className="spinner" /></div>;

  return (
    <div className="mobility-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Mobilité et Transports</h1>
          <p className="page-subtitle">Impact du trafic sur la qualité de l'air</p>
        </div>
      </div>

      <div className="mobility-kpi-grid">
        <div className="card mobility-kpi">
          <div className="mobility-kpi-icon" style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', color: 'var(--danger)' }}>
            <Car size={24} />
          </div>
          <div className="mobility-kpi-content">
            <span className="mobility-kpi-label">Trafic Routier (Congestion)</span>
            <div className="mobility-kpi-val">
              <strong>78%</strong>
              <span className="trend-up"><TrendingUp size={14} /> +12%</span>
            </div>
          </div>
        </div>
        
        <div className="card mobility-kpi">
          <div className="mobility-kpi-icon" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: 'var(--secondary)' }}>
            <Bus size={24} />
          </div>
          <div className="mobility-kpi-content">
            <span className="mobility-kpi-label">Fréquentation Transports (Bus/Tram)</span>
            <div className="mobility-kpi-val">
              <strong>65%</strong>
              <span className="trend-down"><TrendingDown size={14} /> -5%</span>
            </div>
          </div>
        </div>

        <div className="card mobility-kpi">
          <div className="mobility-kpi-icon" style={{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
            <AlertTriangle size={24} />
          </div>
          <div className="mobility-kpi-content">
            <span className="mobility-kpi-label">Incidents Signalés</span>
            <div className="mobility-kpi-val">
              <strong>3</strong>
              <span className="trend-flat">Stagnant</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Corrélation Trafic & Pollution (Aujourd'hui)</h2>
        </div>
        <div className="mobility-chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <ComposedChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="time" tick={{ fill: 'var(--text-muted)' }} />
              <YAxis yAxisId="left" tick={{ fill: 'var(--text-muted)' }} label={{ value: 'Index', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fill: 'var(--text-muted)' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)', borderRadius: '8px' }}
                itemStyle={{ fontSize: '13px' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar yAxisId="left" dataKey="congestion" name="Congestion Routière" fill="var(--danger)" opacity={0.8} radius={[4, 4, 0, 0]} barSize={40} />
              <Bar yAxisId="left" dataKey="transportUsage" name="Usage Transports Communs" fill="var(--secondary)" opacity={0.8} radius={[4, 4, 0, 0]} barSize={40} />
              <Line yAxisId="right" type="monotone" dataKey="pollutionImpact" name="Impact Pollution (PM2.5)" stroke="#a855f7" strokeWidth={3} dot={{ r: 5, fill: '#a855f7' }} activeDot={{ r: 7 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mobility-recommendations card">
        <h3 className="panel-title">Recommandations de Mobilité</h3>
        <ul className="mobility-list">
          <li><strong>Pic de pollution attendu à 18h00 :</strong> Privilégiez le télétravail ou décalez vos horaires de départ.</li>
          <li><strong>Transports en commun :</strong> Réduction tarifaire activée en raison des niveaux de PM10 élevés.</li>
          <li><strong>Zone à Faibles Émissions (ZFE) :</strong> Contrôles renforcés dans le centre-ville aujourd'hui.</li>
        </ul>
      </div>
    </div>
  );
}
