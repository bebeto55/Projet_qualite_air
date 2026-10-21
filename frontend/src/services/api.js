// API service layer – calls the Smart City FastAPI backend (Back/api)
// Set VITE_API_BASE_URL in .env to override (default: http://localhost:8080/api)

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api';
const TOKEN_KEY = 'smart_city_token';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// ── Generic fetch wrapper ────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError('Backend injoignable — vérifiez que l\'API est démarrée (port 8080)', 0);
  }
  if (res.status === 401 && token && !path.startsWith('/auth/login')) {
    localStorage.removeItem(TOKEN_KEY);
    window.dispatchEvent(new Event('smart-city:unauthorized'));
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    const msg = err.message || (Array.isArray(err.detail) ? 'Données invalides' : err.detail) || `HTTP ${res.status}`;
    throw new ApiError(msg, res.status);
  }
  return res.json();
}

// ── Auth (JWT) ───────────────────────────────────────────────────────────────
export const authService = {
  login: (credentials) => apiFetch('/auth/login', { method: 'POST', body: JSON.stringify(credentials) }),
  logout: () => { localStorage.removeItem(TOKEN_KEY); },
  me: () => apiFetch('/auth/me'),
};

// ── Air Quality (Supabase via backend) ───────────────────────────────────────
export const airQualityService = {
  getCurrent:  (sensorId) => apiFetch(`/air-quality/current${sensorId ? `?sensor_id=${encodeURIComponent(sensorId)}` : ''}`),
  getHistory:  (hours = 24, sensorId) =>
    apiFetch(`/air-quality/history?hours=${hours}${sensorId ? `&sensor_id=${encodeURIComponent(sensorId)}` : ''}`),
  getSensors:  () => apiFetch('/sensors'),
  getAnomalies: () => apiFetch('/anomalies'),

  // Predictions from backend ML model (24 models, horizon 1..24h)
  getPredictions: () => apiFetch('/predictions'),
  refreshPredictions: () => apiFetch('/predictions/refresh', { method: 'POST' }),

  // Alerts
  getAlerts: () => apiFetch('/alerts'),
  acknowledgeAlert: (id) => apiFetch(`/alerts/${encodeURIComponent(id)}/acknowledge`, { method: 'POST' }),
  getAlertConfig: () => apiFetch('/alerts/config'),
  updateAlertConfig: (config) => apiFetch('/alerts/config', { method: 'PUT', body: JSON.stringify(config) }),
  testAlertEmail: () => apiFetch('/alerts/test-email', { method: 'POST' }),
  getSentEmails: () => apiFetch('/alerts/emails'),
};

// ── Weather (collected with measures, Open-Meteo) ────────────────────────────
export const weatherService = {
  getCurrent: () => apiFetch('/weather/current'),
};

// ── Admin / monitoring ───────────────────────────────────────────────────────
export const adminService = {
  health:  () => apiFetch('/health'),
  metrics: () => apiFetch('/metrics'),
  logs:    (level) => apiFetch(`/logs?limit=300${level ? `&level=${level}` : ''}`),
};

// ── Power BI ─────────────────────────────────────────────────────────────────
export const powerBiService = {
  // Returns { token, embedUrl, reportId }
  getEmbedConfig: () => apiFetch('/powerbi/embed-config'),
  // Returns full BI analytics from Supabase
  getAnalytics: (hours = 192) => apiFetch(`/powerbi/analytics?hours=${hours}`),
  // Connects PostgreSQL credentials to Power BI Service
  connectDatasource: () => apiFetch('/powerbi/connect-datasource', { method: 'POST' }),
  // Installs Back/prod-ca-2021.crt into Windows Root CA store for Power BI Gateway/Desktop
  installSslCert: () => apiFetch('/powerbi/install-ssl-cert', { method: 'POST' }),
};
