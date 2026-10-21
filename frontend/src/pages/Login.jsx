import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Leaf, Eye, EyeOff, Lock, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './Login.css';

// Demo credentials (replace with real auth)
const DEMO_USERS = [
  { username: 'admin', password: 'admin123', name: 'Marie Dubois', role: 'Responsable Environnement' },
  { username: 'elu',   password: 'elu123',   name: 'Pierre Lambert', role: 'Élu Municipal' },
  { username: 'demo',  password: 'demo',     name: 'Jean Martin',   role: 'Citoyen' },
];

export default function Login() {
  const { isAuthenticated, login } = useAuth();
  const [form, setForm]         = useState({ username: '', password: '' });
  const [showPwd, setShowPwd]   = useState(false);
  const [loading, setLoading]   = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form);
    } catch (err) {
      toast.error(err.message || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (u) => setForm({ username: u.username, password: u.password });

  return (
    <div className="login-screen">
      <div className="login-card">
        {/* Logo */}
        <div className="login-logo">
          <div className="login-logo-icon"><Leaf size={24} /></div>
          <h1>SmartCity</h1>
          <p>Plateforme de surveillance environnementale</p>
        </div>

        {/* Form */}
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Identifiant</label>
            <div className="input-wrap">
              <User size={16} className="input-icon" />
              <input
                type="text"
                placeholder="admin, elu, demo…"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                required
                autoComplete="username"
              />
            </div>
          </div>

          <div className="input-group">
            <label>Mot de passe</label>
            <div className="input-wrap">
              <Lock size={16} className="input-icon" />
              <input
                type={showPwd ? 'text' : 'password'}
                placeholder="••••••••"
                value={form.password}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                required
                autoComplete="current-password"
              />
              <button type="button" className="show-pwd" onClick={() => setShowPwd(s => !s)}>
                {showPwd ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          <button type="submit" className="btn btn-primary login-btn" disabled={loading}>
            {loading ? <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> : 'Se connecter'}
          </button>
        </form>

        {/* Demo credentials */}
        <div className="demo-section">
          <div className="demo-label">Comptes de démonstration :</div>
          <div className="demo-users">
            {DEMO_USERS.map(u => (
              <button key={u.username} className="demo-user-btn" onClick={() => fillDemo(u)}>
                <strong>{u.name}</strong>
                <span>{u.role}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Background decoration */}
      <div className="login-bg">
        <div className="bg-circle c1" />
        <div className="bg-circle c2" />
        <div className="bg-circle c3" />
      </div>
    </div>
  );
}
