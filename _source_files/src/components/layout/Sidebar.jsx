import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Wind, Map, TrendingUp, Bell, FileText,
  BarChart2, Settings, LogOut, Menu, X, ChevronRight, Leaf
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './Sidebar.css';

const NAV = [
  { to: '/',            icon: LayoutDashboard, label: 'Tableau de bord' },
  { to: '/air-quality', icon: Wind,            label: 'Qualité de l\'air' },
  { to: '/map',         icon: Map,             label: 'Carte interactive' },
  { to: '/predictions', icon: TrendingUp,      label: 'Prédictions IA' },
  { to: '/alerts',      icon: Bell,            label: 'Alertes',      badge: true },
  { to: '/mobility',    icon: BarChart2,       label: 'Mobilité' },
  { to: '/reports',     icon: FileText,        label: 'Rapports' },
  { to: '/powerbi',     icon: BarChart2,       label: 'Power BI' },
  { to: '/settings',    icon: Settings,        label: 'Paramètres' },
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
          {NAV.map(({ to, icon: Icon, label, badge }) => (
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
          <button className="icon-btn logout-btn" onClick={handleLogout} title="Déconnexion">
            <LogOut size={16} />
          </button>
        </div>
      </aside>
    </>
  );
}
