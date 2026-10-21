import { useState, useEffect } from 'react';
import { useAirQuality } from '../hooks/useAirQuality';
import { useAuth } from '../context/AuthContext';
import { airQualityService } from '../services/api';
import AlertPanel from '../components/alerts/AlertPanel';
import { Bell, Settings, Mail, Smartphone, Send } from 'lucide-react';
import toast from 'react-hot-toast';
import './Alerts.css';

const THRESHOLDS_DEFAULT = {
  pm25: 50, pm10: 80, no2: 200, o3: 100,
};

export default function Alerts() {
  const { alerts, acknowledgeAlert, refresh } = useAirQuality();
  const { isAdmin } = useAuth();
  const [thresholds, setThresholds] = useState(THRESHOLDS_DEFAULT);
  const [notif, setNotif]           = useState({ email: true, sms: false });
  const [email, setEmail]           = useState('marie.dubois@metropole.fr');
  const [saving, setSaving]         = useState(false);
  const [lastMail, setLastMail]     = useState(null);

  useEffect(() => {
    airQualityService.getAlertConfig()
      .then(cfg => {
        if (cfg?.thresholds) setThresholds(cfg.thresholds);
        if (cfg?.notifications) setNotif(cfg.notifications);
        if (cfg?.recipients?.length) setEmail(cfg.recipients.join(', '));
      })
      .catch(() => {});
  }, []);

  const handleAck = async (id) => {
    try {
      await acknowledgeAlert(id);
      toast.success('Alerte acquittée');
    } catch (e) {
      toast.error(e.message || 'Erreur lors de l\'acquittement');
    }
  };

  const handleSave = async () => {
    if (!isAdmin) {
      toast.error('Seul un administrateur peut modifier les seuils');
      return;
    }
    setSaving(true);
    try {
      const recipients = email.split(',').map(s => s.trim()).filter(Boolean);
      await airQualityService.updateAlertConfig({
        thresholds,
        notifications: notif,
        recipients,
      });
      await refresh();
      toast.success('Configuration des alertes sauvegardée !');
    } catch (e) {
      toast.error(e.message || 'Échec de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleTestEmail = async () => {
    try {
      const res = await airQualityService.testAlertEmail();
      if (res?.email) setLastMail(res.email);
      toast.success('Notification e-mail envoyée et enregistrée !');
    } catch (e) {
      toast.error(e.message || 'Échec de l\'envoi de l\'e-mail');
    }
  };

  return (
    <div className="alerts-page fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Gestion des alertes</h1>
          <p className="page-subtitle">Configuration des seuils, anomalies Z-score et notifications</p>
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
            <h2 className="card-title">Alertes & Anomalies en cours</h2>
          </div>
          <AlertPanel alerts={alerts} onAcknowledge={handleAck} />
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
                    min={1}
                    disabled={!isAdmin}
                    onChange={e => setThresholds(t => ({ ...t, [key]: +e.target.value }))}
                    className="threshold-input"
                  />
                  <span className="threshold-unit">µg/m³</span>
                </div>
                <input type="range" min={1} max={500} value={val}
                  disabled={!isAdmin}
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
                <input type="checkbox" checked={notif.email} disabled={!isAdmin} onChange={e => setNotif(n => ({ ...n, email: e.target.checked }))} />
                <Mail size={15} /> Email
              </label>
              <label className="notif-channel">
                <input type="checkbox" checked={notif.sms} disabled={!isAdmin} onChange={e => setNotif(n => ({ ...n, sms: e.target.checked }))} />
                <Smartphone size={15} /> SMS
              </label>
            </div>

            {notif.email && (
              <div className="input-group">
                <label>Adresse(s) email</label>
                <input
                  type="text"
                  value={email}
                  disabled={!isAdmin}
                  onChange={e => setEmail(e.target.value)}
                  className="email-input"
                  placeholder="email@exemple.fr"
                />
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={handleSave} disabled={!isAdmin || saving}>
              {saving ? 'Sauvegarde…' : 'Sauvegarder la configuration'}
            </button>
            {isAdmin && notif.email && (
              <button className="btn btn-outline" onClick={handleTestEmail} type="button">
                <Send size={14} /> Tester l'e-mail
              </button>
            )}
          </div>

          {lastMail && (
            <div style={{ marginTop: 14, padding: 12, borderRadius: 8, border: '1px solid var(--secondary)', background: 'rgba(16, 185, 129, 0.08)', fontSize: 12 }}>
              <div style={{ fontWeight: 700, color: 'var(--secondary)', marginBottom: 4 }}>
                ✓ Dernier e-mail envoyé ({lastMail.sentAt}) — Destinataire : {lastMail.to?.join(', ')}
              </div>
              <div><strong>Objet :</strong> {lastMail.subject}</div>
              <pre style={{ marginTop: 6, whiteSpace: 'pre-wrap', fontFamily: 'inherit', color: 'var(--text-secondary)' }}>{lastMail.body}</pre>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations by level */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recommandations citoyennes par niveau (Indice Européen EAQI)</h2>
        </div>
        <div className="reco-grid">
          {[
            { level: 'Bon (0–20)', color: '#22c55e', badge: 'good', advice: 'Aucune restriction. Idéal pour les activités extérieures.' },
            { level: 'Correct (20–40)', color: '#84cc16', badge: 'good', advice: 'Qualité de l\'air satisfaisante, profitez de vos activités extérieures.' },
            { level: 'Moyen (40–60)', color: '#f59e0b', badge: 'moderate', advice: 'Personnes sensibles : limitez les efforts prolongés en extérieur.' },
            { level: 'Médiocre (60–80)', color: '#f97316', badge: 'unhealthy-sg', advice: 'Enfants, seniors et asthmatiques : réduisez les activités extérieures.' },
            { level: 'Très médiocre (80–100)', color: '#ef4444', badge: 'unhealthy', advice: 'Port du masque conseillé. Réduisez les activités sportives extérieures.' },
            { level: 'Extrêmement médiocre (>100)', color: '#a855f7', badge: 'very-unhealthy', advice: '🚨 Mesures d\'urgence. Restriction de circulation activée. Restez à l\'intérieur.' },
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
