import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Wind, Map, TrendingUp, Bell, FileText,
  BarChart2, Car, Activity, LogOut, Menu, X, ChevronRight, Leaf
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './Sidebar.css';

const NAV_SECTIONS = [
  {
    title: 'Temps réel',
    items: [
      { to: '/',            icon: LayoutDashboard, label: 'Vue d\'ensemble' },
      { to: '/map',         icon: Map,             label: 'Carte des 34 stations' },
      { to: '/air-quality', icon: Wind,            label: 'Détail polluants' },
    ],
  },
  {
    title: 'Analyse & Prévision',
    items: [
      { to: '/predictions', icon: TrendingUp,      label: 'Prédictions IA (J+1)' },
      { to: '/mobility',    icon: Car,             label: 'Mobilité & Trafic' },
      { to: '/powerbi',     icon: BarChart2,       label: 'Power BI' },
    ],
  },
  {
    title: 'Pilotage & Système',
    items: [
      { to: '/alerts',      icon: Bell,            label: 'Alertes & Seuils', badge: true },
      { to: '/reports',     icon: FileText,        label: 'Rapports Élus (PDF)' },
      { to: '/settings',    icon: Activity,        label: 'Monitoring & Logs' },
    ],
  },
];

export default function Sidebar({ alertCount = 0 }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />}

      {/* Mobile toggle */}
      <button className="sidebar-mobile-toggle" onClick={() => setMobileOpen(true)}>
        <Menu size={22} />
      </button>

      <aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
        {/* Header */}
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="logo-icon"><Leaf size={18} /></div>
            {!collapsed && <span className="logo-text">SmartCity</span>}
          </div>
          <div className="sidebar-controls">
            {mobileOpen && (
              <button className="icon-btn" onClick={() => setMobileOpen(false)}><X size={18} /></button>
            )}
            <button className="icon-btn desktop-only" onClick={() => setCollapsed(c => !c)}>
              <ChevronRight size={16} className={`chevron ${collapsed ? '' : 'rotate'}`} />
            </button>
          </div>
        </div>

        {/* Nav */}
        <nav className="sidebar-nav">
          {NAV_SECTIONS.map(section => (
            <div key={section.title} style={{ display: 'flex', flexDirection: 'column', gap: 2, marginBottom: 10 }}>
              {!collapsed && (
                <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', padding: '6px 12px 2px' }}>
                  {section.title}
                </div>
              )}
              {section.items.map(({ to, icon: Icon, label, badge }) => (
                <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                  onClick={() => setMobileOpen(false)}>
                  <Icon size={18} className="nav-icon" />
                  {!collapsed && <span className="nav-label">{label}</span>}
                  {badge && alertCount > 0 && !collapsed && (
                    <span className="nav-badge">{alertCount}</span>
                  )}
                  {badge && alertCount > 0 && collapsed && (
                    <span className="nav-badge-dot" />
                  )}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        {/* User footer */}
        <div className="sidebar-footer">
          {user && (
            <div className="user-info">
              <div className="user-avatar">{user.name?.[0]?.toUpperCase() || 'U'}</div>
              {!collapsed && (
                <div className="user-details">
                  <span className="user-name">{user.name || 'Admin'}</span>
                  <span className="user-role">{user.role || 'Responsable'}</span>
                </div>
              )}
            </div>
          )}
          <button
            className="btn btn-outline logout-btn"
            onClick={handleLogout}
            title="Déconnexion"
            style={{ width: collapsed ? 'auto' : '100%', justifyContent: 'center', marginTop: 8, color: 'var(--danger)', borderColor: 'rgba(239,68,68,0.35)', fontSize: 12, padding: '6px 10px' }}
          >
            <LogOut size={15} />
            {!collapsed && <span>Se déconnecter</span>}
          </button>
        </div>
      </aside>
    </>
  );
}
