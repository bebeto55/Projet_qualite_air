import { Bell, RefreshCw, Wifi, LogOut, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAirQuality } from '../../hooks/useAirQuality';
import { useAuth } from '../../context/AuthContext';
import { formatTime } from '../../utils/airQuality';
import './Topbar.css';

export default function Topbar() {
  const { lastRefresh, refresh, loading, alerts } = useAirQuality();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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

        <button className="icon-btn notif-btn" title="Alertes" onClick={() => navigate('/alerts')}>
          <Bell size={16} />
          {alerts?.length > 0 && <span className="notif-count">{alerts.length}</span>}
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, paddingLeft: 10, borderLeft: '1px solid var(--border)' }}>
          <span style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 5 }}>
            <User size={14} /> <strong>{user?.name || 'Admin'}</strong>
          </span>
          <button
            className="btn btn-outline"
            onClick={handleLogout}
            style={{ padding: '6px 12px', fontSize: 12, fontWeight: 600, color: '#fff', background: 'rgba(239,68,68,0.85)', borderColor: 'var(--danger)' }}
            title="Se déconnecter de l'application"
          >
            <LogOut size={14} /> Déconnexion
          </button>
        </div>
      </div>
    </header>
  );
}
