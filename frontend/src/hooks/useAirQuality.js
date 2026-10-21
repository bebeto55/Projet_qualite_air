import { useState, useEffect, useCallback, useRef } from 'react';
import { airQualityService, weatherService } from '../services/api';

/**
 * Live + historical air quality data from the backend (Supabase `mesures` table,
 * 34 stations Île-de-France, refreshed every 30 min by the collection pipeline).
 */
export function useAirQuality(refreshMs = 60_000, historyHours = 48) {
  const [current,     setCurrent]     = useState(null);
  const [history,     setHistory]     = useState([]);
  const [sensors,     setSensors]     = useState([]);
  const [alerts,      setAlerts]      = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const intervalRef = useRef(null);

  const fetchData = useCallback(async () => {
    try {
      const [cur, hist, sens, alr] = await Promise.all([
        airQualityService.getCurrent(),
        airQualityService.getHistory(historyHours),
        airQualityService.getSensors(),
        airQualityService.getAlerts(),
      ]);
      setCurrent(cur);
      setHistory(hist);
      setSensors(sens);
      setAlerts(alr);
      setLastRefresh(new Date());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [historyHours]);

  useEffect(() => {
    fetchData();
    intervalRef.current = setInterval(fetchData, refreshMs);
    return () => clearInterval(intervalRef.current);
  }, [fetchData, refreshMs]);

  const acknowledgeAlert = useCallback(async (id) => {
    await airQualityService.acknowledgeAlert(id);
    setAlerts(a => a.filter(x => x.id !== id));
  }, []);

  return { current, history, sensors, alerts, loading, error, lastRefresh, refresh: fetchData, acknowledgeAlert };
}

/** Variation (%) between the last value and the value `hoursBack` hours earlier. */
export function computeTrend(history, key, hoursBack = 24) {
  const pts = history.filter(h => h[key] != null);
  if (pts.length < 2) return undefined;
  const last = pts[pts.length - 1][key];
  const ref  = pts[Math.max(0, pts.length - 1 - hoursBack)][key];
  if (!ref) return undefined;
  return +(((last - ref) / ref) * 100).toFixed(1);
}

/** 24h AQI forecast computed by the ML model (24 XGBoost models, one per horizon). */
export function usePredictions() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  const load = useCallback(async (force = false) => {
    setLoading(true);
    try {
      const res = force ? await airQualityService.refreshPredictions() : await airQualityService.getPredictions();
      setData(res);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return { data, predictions: data?.city ?? [], loading, error, reload: load };
}

export function useWeather() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    weatherService.getCurrent()
      .then(setWeather)
      .catch(() => setWeather(null))
      .finally(() => setLoading(false));
  }, []);

  return { weather, loading };
}
