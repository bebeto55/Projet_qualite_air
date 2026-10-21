// ─── AQI Calculation Utilities ───────────────────────────────────────────────

// European Air Quality Index (EAQI) — the scale returned by Open-Meteo / the backend
export const AQI_LEVELS = [
  { max: 20,  label: 'Bon',                 badge: 'good',           color: '#22c55e', recommendation: 'Conditions idéales pour les activités extérieures.' },
  { max: 40,  label: 'Correct',             badge: 'good',           color: '#84cc16', recommendation: 'Qualité de l\'air satisfaisante, profitez de vos activités extérieures.' },
  { max: 60,  label: 'Moyen',               badge: 'moderate',       color: '#f59e0b', recommendation: 'Les personnes sensibles devraient limiter les efforts prolongés en extérieur.' },
  { max: 80,  label: 'Médiocre',            badge: 'unhealthy-sg',   color: '#f97316', recommendation: 'Enfants, seniors et asthmatiques : réduisez les activités extérieures.' },
  { max: 100, label: 'Très médiocre',       badge: 'unhealthy',      color: '#ef4444', recommendation: 'Tout le monde devrait réduire les activités physiques en extérieur.' },
  { max: Infinity, label: 'Extrêmement médiocre', badge: 'very-unhealthy', color: '#a855f7', recommendation: 'Évitez toute activité extérieure, restez à l\'intérieur.' },
];
export const AQI_SCALE_MAX = 120;

export function getAqiLevel(aqi) {
  return AQI_LEVELS.find(l => (aqi ?? 0) <= l.max) || AQI_LEVELS[AQI_LEVELS.length - 1];
}

// PM2.5 → AQI (EPA standard breakpoints)
const PM25_BREAKPOINTS = [
  { cLow: 0,     cHigh: 12.0,  iLow: 0,   iHigh: 50  },
  { cLow: 12.1,  cHigh: 35.4,  iLow: 51,  iHigh: 100 },
  { cLow: 35.5,  cHigh: 55.4,  iLow: 101, iHigh: 150 },
  { cLow: 55.5,  cHigh: 150.4, iLow: 151, iHigh: 200 },
  { cLow: 150.5, cHigh: 250.4, iLow: 201, iHigh: 300 },
  { cLow: 250.5, cHigh: 500.4, iLow: 301, iHigh: 500 },
];

export function pm25ToAqi(pm25) {
  const bp = PM25_BREAKPOINTS.find(b => pm25 >= b.cLow && pm25 <= b.cHigh);
  if (!bp) return pm25 > 500 ? 500 : 0;
  return Math.round(((bp.iHigh - bp.iLow) / (bp.cHigh - bp.cLow)) * (pm25 - bp.cLow) + bp.iLow);
}

// ─── Pollutant Thresholds (µg/m³) ─────────────────────────────────────────────
export const THRESHOLDS = {
  pm25: { good: 12, moderate: 35.4, bad: 55.4, veryBad: 150.4, unit: 'µg/m³' },
  pm10: { good: 54, moderate: 154,  bad: 254,  veryBad: 354,   unit: 'µg/m³' },
  no2:  { good: 53, moderate: 100,  bad: 200,  veryBad: 300,   unit: 'µg/m³' },
  o3:   { good: 54, moderate: 70,   bad: 85,   veryBad: 105,   unit: 'ppb'   },
  so2:  { good: 35, moderate: 75,   bad: 185,  veryBad: 304,   unit: 'ppb'   },
};

export function getPollutantStatus(pollutant, value) {
  const t = THRESHOLDS[pollutant];
  if (!t) return 'unknown';
  if (value <= t.good)     return 'good';
  if (value <= t.moderate) return 'moderate';
  if (value <= t.bad)      return 'unhealthy-sg';
  if (value <= t.veryBad)  return 'unhealthy';
  return 'very-unhealthy';
}

// ─── Date / Time Helpers ──────────────────────────────────────────────────────
export function formatDate(date) {
  return new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(date));
}

export function formatTime(date) {
  return new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit' }).format(new Date(date));
}

export function formatDateTime(date) {
  return `${formatDate(date)} ${formatTime(date)}`;
}

export function hoursAgo(n) {
  return new Date(Date.now() - n * 3600 * 1000);
}

// ─── Random data generation (simulation) ─────────────────────────────────────
export function generateHistoricalData(hours = 24) {
  const data = [];
  const now = Date.now();
  let pm25 = 22; let pm10 = 40; let no2 = 35; let o3 = 48;
  for (let i = hours; i >= 0; i--) {
    pm25  = Math.max(5,  Math.min(150, pm25  + (Math.random() - 0.48) * 4));
    pm10  = Math.max(10, Math.min(200, pm10  + (Math.random() - 0.48) * 6));
    no2   = Math.max(5,  Math.min(250, no2   + (Math.random() - 0.48) * 5));
    o3    = Math.max(10, Math.min(130, o3    + (Math.random() - 0.48) * 3));
    const temp = 18 + Math.sin((hours - i) / 6) * 6 + (Math.random() - 0.5) * 2;
    const humidity = 55 + Math.cos((hours - i) / 8) * 15 + (Math.random() - 0.5) * 5;
    data.push({
      time: new Date(now - i * 3600 * 1000).toISOString(),
      timeLabel: new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit' }).format(new Date(now - i * 3600 * 1000)),
      pm25: +pm25.toFixed(1),
      pm10: +pm10.toFixed(1),
      no2:  +no2.toFixed(1),
      o3:   +o3.toFixed(1),
      aqi:  pm25ToAqi(pm25),
      temp: +temp.toFixed(1),
      humidity: +Math.max(20, Math.min(100, humidity)).toFixed(1),
    });
  }
  return data;
}

export function generateSensorData() {
  const sensors = [
    { id: 'S01', name: 'Centre-Ville',  lat: 43.2965, lng: 5.3698 },
    { id: 'S02', name: 'Zone Industrielle', lat: 43.3100, lng: 5.3900 },
    { id: 'S03', name: 'Quartier Résidentiel', lat: 43.2800, lng: 5.3500 },
  ];
  return sensors.map(s => ({
    ...s,
    pm25: +(Math.random() * 60 + 5).toFixed(1),
    pm10: +(Math.random() * 80 + 10).toFixed(1),
    no2:  +(Math.random() * 120 + 10).toFixed(1),
    o3:   +(Math.random() * 80 + 20).toFixed(1),
    temp: +(Math.random() * 15 + 15).toFixed(1),
    humidity: +(Math.random() * 40 + 40).toFixed(1),
    lastUpdate: new Date().toISOString(),
    status: Math.random() > 0.1 ? 'online' : 'offline',
  }));
}

export function generatePredictionData(days = 7) {
  const data = [];
  let basePm25 = 25;
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() + i);
    basePm25 = Math.max(8, Math.min(80, basePm25 + (Math.random() - 0.5) * 10));
    const lower = Math.max(0, basePm25 - 8 - Math.random() * 5);
    const upper = basePm25 + 8 + Math.random() * 5;
    data.push({
      date: date.toISOString().split('T')[0],
      dateLabel: new Intl.DateTimeFormat('fr-FR', { weekday: 'short', day: '2-digit', month: 'short' }).format(date),
      predicted: +basePm25.toFixed(1),
      lower: +lower.toFixed(1),
      upper: +upper.toFixed(1),
      aqi: pm25ToAqi(basePm25),
      confidence: +(85 - i * 5 + Math.random() * 5).toFixed(0),
    });
  }
  return data;
}
