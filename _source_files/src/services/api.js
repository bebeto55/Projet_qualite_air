// API service layer – calls the backend REST API
// All endpoints are relative; set VITE_API_BASE_URL in .env to override

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api';
const AQICN_TOKEN = import.meta.env.VITE_AQICN_TOKEN || 'demo';
const OWM_KEY    = import.meta.env.VITE_OWM_KEY    || '';

// ── Generic fetch wrapper ────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('smart_city_token');
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.message || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authService = {
  login: (credentials) => apiFetch('/auth/login', { method: 'POST', body: JSON.stringify(credentials) }),
  logout: () => { localStorage.removeItem('smart_city_token'); },
  me: () => apiFetch('/auth/me'),
};

// ── Air Quality (backend proxy + AQICN direct fallback) ───────────────────────
export const airQualityService = {
  // Current reading for a station
  getCurrent: (city = 'marseille') =>
    fetch(`https://api.waqi.info/feed/${city}/?token=${AQICN_TOKEN}`)
      .then(r => r.json())
      .then(d => d.data),

  // Historical from backend
  getHistory: (hours = 24) => apiFetch(`/air-quality/history?hours=${hours}`),

  // Sensor list from backend
  getSensors: () => apiFetch('/sensors'),

  // Predictions from backend ML model
  getPredictions: () => apiFetch('/predictions'),

  // Alerts
  getAlerts: () => apiFetch('/alerts'),
  acknowledgeAlert: (id) => apiFetch(`/alerts/${id}/acknowledge`, { method: 'POST' }),
  getAlertConfig: () => apiFetch('/alerts/config'),
  updateAlertConfig: (config) => apiFetch('/alerts/config', { method: 'PUT', body: JSON.stringify(config) }),
};

// ── Weather ───────────────────────────────────────────────────────────────────
export const weatherService = {
  getCurrent: (lat = 43.2965, lon = 5.3698) =>
    OWM_KEY
      ? fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${OWM_KEY}&units=metric&lang=fr`)
          .then(r => r.json())
      : apiFetch('/weather/current'),

  getForecast: (lat = 43.2965, lon = 5.3698) =>
    OWM_KEY
      ? fetch(`https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${OWM_KEY}&units=metric&lang=fr`)
          .then(r => r.json())
      : apiFetch('/weather/forecast'),
};

// ── Mobility ──────────────────────────────────────────────────────────────────
export const mobilityService = {
  getTraffic: () => apiFetch('/mobility/traffic'),
  getTransport: () => apiFetch('/mobility/transport'),
};

// ── Reports ───────────────────────────────────────────────────────────────────
export const reportService = {
  generate: (params) =>
    fetch(`${BASE_URL}/reports/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('smart_city_token')}`,
      },
      body: JSON.stringify(params),
    }).then(r => r.blob()),
};

// ── Power BI ─────────────────────────────────────────────────────────────────
export const powerBiService = {
  // Returns { token, embedUrl, reportId, datasetId }
  getEmbedConfig: () => apiFetch('/powerbi/embed-config'),
};
