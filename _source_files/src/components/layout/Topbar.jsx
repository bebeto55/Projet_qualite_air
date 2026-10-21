import { Bell, RefreshCw, Wifi } from 'lucide-react';
import { useAirQuality } from '../../hooks/useAirQuality';
import { formatTime } from '../../utils/airQuality';
import './Topbar.css';

export default function Topbar() {
  const { lastRefresh, refresh, loading, alerts } = useAirQuality();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <div className="live-indicator">
          <span className="live-dot" />
          <span>En direct</span>
        </div>
        {lastRefresh && (
          <span className="topbar-refresh-time">
            Mis à jour à {formatTime(lastRefresh)}
          </span>
        )}
      </div>

      <div className="topbar-right">
        <div className="topbar-status">
          <Wifi size={14} className="text-success" />
          <span>API connectée</span>
        </div>

        <button className={`icon-btn ${loading ? 'spin-btn' : ''}`} onClick={refresh} title="Rafraîchir">
          <RefreshCw size={16} className={loading ? 'spinning' : ''} />
        </button>

        <button className="icon-btn notif-btn" title="Alertes">
          <Bell size={16} />
          {alerts?.length > 0 && <span className="notif-count">{alerts.length}</span>}
        </button>
      </div>
    </header>
  );
}
