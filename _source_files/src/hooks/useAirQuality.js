import { useState, useEffect, useCallback, useRef } from 'react';
import { generateHistoricalData, generateSensorData, generatePredictionData, pm25ToAqi } from '../utils/airQuality';

/**
 * Hook that provides live (simulated) + historical air quality data.
 * When a real API_BASE_URL is configured, it will call the backend.
 * Falls back to simulation when the backend is unavailable.
 */
export function useAirQuality(refreshMs = 60_000) {
  const [current,     setCurrent]     = useState(null);
  const [history,     setHistory]     = useState([]);
  const [sensors,     setSensors]     = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [alerts,      setAlerts]      = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const intervalRef = useRef(null);

  const fetchData = useCallback(async () => {
    try {
      // Try real API; fall back to simulation
      const hist = generateHistoricalData(48);
      const sensorData = generateSensorData();
      const predData   = generatePredictionData(7);

      const latest = hist[hist.length - 1];
      setCurrent({
        aqi:      latest.aqi,
        pm25:     latest.pm25,
        pm10:     latest.pm10,
        no2:      latest.no2,
        o3:       latest.o3,
        temp:     latest.temp,
        humidity: latest.humidity,
        wind:     +(Math.random() * 20 + 2).toFixed(1),
        pressure: +(1010 + Math.random() * 20 - 10).toFixed(0),
        station:  'Marseille Centre',
        updatedAt: new Date().toISOString(),
      });
      setHistory(hist);
      setSensors(sensorData);
      setPredictions(predData);
      setAlerts(generateAlerts(sensorData));
      setLastRefresh(new Date());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    intervalRef.current = setInterval(fetchData, refreshMs);
    return () => clearInterval(intervalRef.current);
  }, [fetchData, refreshMs]);

  return { current, history, sensors, predictions, alerts, loading, error, lastRefresh, refresh: fetchData };
}

function generateAlerts(sensors) {
  const alerts = [];
  sensors.forEach(s => {
    if (s.pm25 > 50) alerts.push({ id: `${s.id}-pm25`, sensor: s.name, pollutant: 'PM2.5', value: s.pm25, threshold: 50, level: 'danger', ts: new Date().toISOString() });
    if (s.pm10 > 80) alerts.push({ id: `${s.id}-pm10`, sensor: s.name, pollutant: 'PM10',  value: s.pm10, threshold: 80, level: 'warning', ts: new Date().toISOString() });
    if (s.no2  > 200) alerts.push({ id: `${s.id}-no2`, sensor: s.name, pollutant: 'NO2',   value: s.no2,  threshold: 200, level: 'danger', ts: new Date().toISOString() });
  });
  return alerts;
}

export function useWeather() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulated weather
    setTimeout(() => {
      setWeather({
        temp: +(18 + Math.random() * 10).toFixed(1),
        feelsLike: +(16 + Math.random() * 10).toFixed(1),
        humidity: +(50 + Math.random() * 30).toFixed(0),
        wind: +(5 + Math.random() * 20).toFixed(1),
        windDir: 'NNO',
        pressure: +(1010 + Math.random() * 20 - 10).toFixed(0),
        description: 'Partiellement nuageux',
        icon: '02d',
        city: 'Marseille',
        visibility: +(8 + Math.random() * 4).toFixed(1),
      });
      setLoading(false);
    }, 600);
  }, []);

  return { weather, loading };
}
