import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('smart_city_token');
    if (token) {
      authService.me()
        .then(setUser)
        .catch(() => localStorage.removeItem('smart_city_token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // Token expired / revoked on the backend → back to login
  useEffect(() => {
    const onUnauthorized = () => setUser(null);
    window.addEventListener('smart-city:unauthorized', onUnauthorized);
    return () => window.removeEventListener('smart-city:unauthorized', onUnauthorized);
  }, []);

  const login = async (credentials) => {
    const { token, user: u } = await authService.login(credentials);
    localStorage.setItem('smart_city_token', token);
    setUser(u);
    return u;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user, isAdmin: !!user?.is_admin }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
