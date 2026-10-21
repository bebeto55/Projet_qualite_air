import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/layout/Layout';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AirQuality from './pages/AirQuality';
import MapPage from './pages/MapPage';
import Predictions from './pages/Predictions';
import Alerts from './pages/Alerts';
import Mobility from './pages/Mobility';
import Reports from './pages/Reports';
import PowerBIPage from './pages/PowerBIPage';

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="spinner" />
    </div>;
  }
  
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" toastOptions={{ 
          style: { background: '#1e293b', color: '#f1f5f9', border: '1px solid #334155' } 
        }} />
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Dashboard />} />
            <Route path="air-quality" element={<AirQuality />} />
            <Route path="map" element={<MapPage />} />
            <Route path="predictions" element={<Predictions />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="mobility" element={<Mobility />} />
            <Route path="reports" element={<Reports />} />
            <Route path="powerbi" element={<PowerBIPage />} />
            {/* Fallback settings page for now */}
            <Route path="settings" element={
              <div className="fade-in" style={{ padding: 20 }}>
                <h1>Paramètres</h1>
                <p style={{ color: 'var(--text-muted)' }}>Page en construction.</p>
              </div>
            } />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
