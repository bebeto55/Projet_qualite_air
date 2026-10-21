import { useState } from 'react';
import { useAirQuality } from '../hooks/useAirQuality';
import AlertPanel from '../components/alerts/AlertPanel';
import { Bell, Settings, Mail, Smartphone } from 'lucide-react';
import toast from 'react-hot-toast';
import './Alerts.css';

const THRESHOLDS_DEFAULT = {
  pm25: 50, pm10: 80, no2: 200, o3: 100,
};

export default function Alerts() {
  const { alerts } = useAirQuality();
  const [thresholds, setThresholds] = useState(THRESHOLDS_DEFAULT);
  const [notif, setNotif]         = useState({ email: true, sms: false });
  const [email, setEmail]         = useState('marie.dubois@metropole.fr');
  const [saved, setSaved]         = useState(false);

  const handleSave = () => {
    toast.success('Configuration des alertes sauvegardée !');
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="alerts-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Gestion des alertes</h1>
          <p className="page-subtitle">Configuration des seuils et notifications</p>
        </div>
        <div className="alert-count-badge">
          <Bell size={16} />
          {alerts.length} alerte{alerts.length !== 1 ? 's' : ''} active{alerts.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="alerts-grid">
        {/* Active alerts */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Alertes en cours</h2>
          </div>
          <AlertPanel alerts={alerts} onAcknowledge={() => toast.success('Alerte acquittée')} />
        </div>

        {/* Threshold config */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title"><Settings size={15} /> Seuils d'alerte</h2>
          </div>
          <div className="threshold-form">
            {Object.entries(thresholds).map(([key, val]) => (
              <div key={key} className="threshold-row">
                <label className="threshold-label">{key.toUpperCase()}</label>
                <div className="threshold-input-wrap">
                  <input
                    type="number"
                    value={val}
                    min={0}
                    onChange={e => setThresholds(t => ({ ...t, [key]: +e.target.value }))}
                    className="threshold-input"
                  />
                  <span className="threshold-unit">µg/m³</span>
                </div>
                <input type="range" min={0} max={500} value={val}
                  onChange={e => setThresholds(t => ({ ...t, [key]: +e.target.value }))}
                  className="threshold-range"
                  style={{ '--pct': `${(val/500)*100}%` }}
                />
              </div>
            ))}
          </div>

          {/* Notification channels */}
          <div className="notif-section">
            <h3 className="notif-title">Canaux de notification</h3>
            <div className="notif-channels">
              <label className="notif-channel">
                <input type="checkbox" checked={notif.email} onChange={e => setNotif(n => ({ ...n, email: e.target.checked }))} />
                <Mail size={15} /> Email
              </label>
              <label className="notif-channel">
                <input type="checkbox" checked={notif.sms} onChange={e => setNotif(n => ({ ...n, sms: e.target.checked }))} />
                <Smartphone size={15} /> SMS
              </label>
            </div>

            {notif.email && (
              <div className="input-group">
                <label>Adresse email</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  className="email-input"
                  placeholder="email@exemple.fr"
                />
              </div>
            )}
          </div>

          <button className="btn btn-primary" onClick={handleSave}>
            Sauvegarder la configuration
          </button>
        </div>
      </div>

      {/* Recommendations by level */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recommandations citoyennes par niveau</h2>
        </div>
        <div className="reco-grid">
          {[
            { level: 'Bon', color: '#22c55e', badge: 'good', advice: 'Aucune restriction. Idéal pour les activités extérieures.' },
            { level: 'Modéré', color: '#f59e0b', badge: 'moderate', advice: 'Personnes sensibles : limitez les efforts prolongés en extérieur.' },
            { level: 'Mauvais', color: '#ef4444', badge: 'unhealthy', advice: 'Port du masque conseillé. Réduisez les activités sportives extérieures.' },
            { level: 'Très mauvais', color: '#a855f7', badge: 'very-unhealthy', advice: 'Restez à l\'intérieur. Aérez brièvement les logements.' },
            { level: 'Dangereux', color: '#7f1d1d', badge: 'hazardous', advice: '🚨 Mesures d\'urgence. Restriction de circulation activée. Restez chez vous.' },
          ].map(r => (
            <div key={r.level} className="reco-card" style={{ borderColor: r.color, background: `${r.color}11` }}>
              <span className={`badge badge-${r.badge}`}>{r.level}</span>
              <p>{r.advice}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
