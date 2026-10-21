import { AlertTriangle, X, CheckCircle, Clock } from 'lucide-react';
import { formatDateTime } from '../../utils/airQuality';
import './AlertPanel.css';

const LEVEL_CONFIG = {
  danger:  { icon: AlertTriangle, color: 'var(--danger)',  bg: 'rgba(239,68,68,.12)'  },
  warning: { icon: AlertTriangle, color: 'var(--warning)', bg: 'rgba(245,158,11,.12)' },
  info:    { icon: CheckCircle,   color: 'var(--primary)', bg: 'rgba(14,165,233,.12)' },
};

export default function AlertPanel({ alerts = [], onAcknowledge }) {
  if (alerts.length === 0) {
    return (
      <div className="alert-empty">
        <CheckCircle size={32} color="var(--secondary)" />
        <span>Aucune alerte active</span>
      </div>
    );
  }

  return (
    <div className="alert-panel">
      {alerts.map(alert => {
        const cfg = LEVEL_CONFIG[alert.level] || LEVEL_CONFIG.info;
        const Icon = cfg.icon;
        return (
          <div key={alert.id} className="alert-item" style={{ background: cfg.bg, borderColor: cfg.color }}>
            <div className="alert-icon" style={{ color: cfg.color }}>
              <Icon size={18} />
            </div>
            <div className="alert-body">
              <div className="alert-title">
                {alert.type === 'anomaly'
                  ? <><strong>{alert.pollutant}</strong> mesure anormale sur <strong>{alert.sensor}</strong></>
                  : <><strong>{alert.pollutant}</strong> dépassement sur <strong>{alert.sensor}</strong></>}
              </div>
              <div className="alert-detail">
                Valeur : <span style={{ color: cfg.color, fontWeight: 600 }}>{alert.value} µg/m³</span>
                {alert.type === 'anomaly'
                  ? <>&nbsp;— Moyenne 7j : {alert.mean} µg/m³ (z = {alert.zScore})</>
                  : <>&nbsp;— Seuil : {alert.threshold} µg/m³</>}
              </div>
              <div className="alert-time">
                <Clock size={11} />
                {formatDateTime(alert.ts)}
              </div>
            </div>
            {onAcknowledge && (
              <button className="alert-ack" onClick={() => onAcknowledge(alert.id)} title="Acquitter">
                <X size={14} />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
