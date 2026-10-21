import { useState, useMemo } from 'react';
import { PowerBIEmbed } from 'powerbi-client-react';
import { models } from 'powerbi-client';
import {
  ResponsiveContainer, ComposedChart, AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell,
} from 'recharts';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getAqiLevel, formatDateTime } from '../../utils/airQuality';
import { powerBiService, airQualityService } from '../../services/api';
import AqiGauge from '../dashboard/AqiGauge';
import toast from 'react-hot-toast';
import './PowerBIPanel.css';

const SMART_CITY_PAGES = [
  { id: 'presentation', label: '1. Présentation' },
  { id: 'stats_aqi',    label: '2. Statistiques aqi' },
  { id: 'autres',       label: '3. autres données' },
  { id: 'carte',        label: '4. Carte' },
  { id: 'actualite',    label: '5. Actualité' },
  { id: 'previsions',   label: '6. prévisions' },
];

const EAQI_REF_TABLE = [
  { min: 0,  max: 20,  color: '#22c55e', colorName: 'Vert',       qualite: 'Bon' },
  { min: 20, max: 40,  color: '#84cc16', colorName: 'Vert clair', qualite: 'Correct' },
  { min: 40, max: 60,  color: '#eab308', colorName: 'Jaune',      qualite: 'Moyen / Modéré' },
  { min: 60, max: 80,  color: '#f97316', colorName: 'Orange',     qualite: 'Médiocre / Mauvais' },
  { min: 80, max: 100, color: '#ef4444', colorName: 'Rouge',      qualite: 'Très mauvais' },
  { min: 100, max: 500, color: '#7f1d1d', colorName: 'Bordeaux',  qualite: 'Extrêmement mauvais' },
];

export default function PowerBIPanel({ embedConfig, analytics }) {
  const hasSdkConfig = Boolean(embedConfig?.embedUrl && (embedConfig?.accessToken || embedConfig?.token) && embedConfig?.reportId);
  const [mode, setMode]             = useState('smartcity'); // 'smartcity' | 'embed' | 'live' | 'sweetviz'
  const [pbiTab, setPbiTab]         = useState('presentation');
  const [embedState, setEmbedState] = useState('loading');
  const [activePage, setActivePage] = useState(embedConfig?.pages?.[0]?.name || '');
  const [selectedSensor, setSelectedSensor] = useState('ALL');
  const [maxHorizon, setMaxHorizon] = useState(24);
  const [stationForecast, setStationForecast] = useState(null);
  const [search, setSearch]         = useState('');

  const stations = analytics?.stationStats || [];
  const selectedStationObj = useMemo(() => {
    if (selectedSensor === 'ALL') return stations[0] || null;
    return stations.find(s => s.name === selectedSensor || s.id === selectedSensor) || stations[0] || null;
  }, [stations, selectedSensor]);

  const handleSelectSensorForForecast = async (sensorName) => {
    setSelectedSensor(sensorName);
    const st = stations.find(s => s.name === sensorName);
    if (st) {
      try {
        const res = await airQualityService.getCurrent(st.id);
        setStationForecast(res);
      } catch {
        // ignore
      }
    }
  };

  const switchPbiPage = async (pageName) => {
    setActivePage(pageName);
    if (window._pbiReport && typeof window._pbiReport.setPage === 'function') {
      try {
        await window._pbiReport.setPage(pageName);
      } catch (e) {
        console.error('Switch page error:', e);
      }
    }
  };

  const handleInstallSslCert = async () => {
    try {
      const res = await powerBiService.installSslCert();
      if (res.ok) {
        toast.success('Certificat SSL Supabase (prod-ca-2021.crt) installé dans Windows Root CA !');
      } else {
        toast.error(res.output || 'Échec installation certificat');
      }
    } catch (e) {
      toast.error(e.message || 'Erreur lors de l\'installation du certificat');
    }
  };

  const handleConnectPostgres = async () => {
    try {
      const res = await powerBiService.connectDatasource();
      toast.success(res.message || 'Source PostgreSQL connectée !');
      if (window._pbiReport && typeof window._pbiReport.reload === 'function') {
        await window._pbiReport.reload();
      }
    } catch (e) {
      toast.error(e.message || 'Échec de connexion sur Power BI Cloud');
    }
  };

  const filteredRawRows = useMemo(() => {
    const rows = analytics?.rawTable || [];
    if (selectedSensor === 'ALL') return rows;
    return rows.filter(r => r.capteur_nom === selectedSensor);
  }, [analytics, selectedSensor]);

  const stationStats = stations.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase())
  );
  const top10Stations = stations.slice(0, 10);
  const forecastSeries = (analytics?.forecast24h || []).slice(0, maxHorizon).map((f, idx) => ({
    ...f,
    heureNum: idx + 1,
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
      {/* Barre de sélection du mode */}
      <div className="card" style={{ padding: '12px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button
            className={`btn ${mode === 'smartcity' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setMode('smartcity')}
          >
            📊 Rapport Smart_City (6 pages · Direct Supabase)
          </button>
          <button
            className={`btn ${mode === 'embed' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setMode('embed')}
          >
            ☁️ Power BI Service Cloud + Certificat SSL Passerelle
          </button>
          <button
            className={`btn ${mode === 'live' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setMode('live')}
          >
            📈 Corrélations & Top Stations
          </button>
          <button
            className={`btn ${mode === 'sweetviz' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setMode('sweetviz')}
          >
            🔬 Rapport EDA (Sweetviz)
          </button>
        </div>
        {analytics?.fromDate && (
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            Période : {formatDateTime(analytics.fromDate)} → {formatDateTime(analytics.toDate)}
          </span>
        )}
      </div>

      {/* ═══════════════════════════════════════════════════════════════════════
          MODE 1 : RAPPORT SMART_CITY (LES 6 PAGES EXACTES DU PBIX SUR SUPABASE)
         ═══════════════════════════════════════════════════════════════════════ */}
      {mode === 'smartcity' && analytics && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Barre d'onglets Power BI (identique aux 6 pages de Smart_City.pbix) */}
          <div className="card" style={{ padding: '10px 14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, borderLeft: '4px solid #f59e0b' }}>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontSize: 12, fontWeight: 700, color: '#f59e0b', marginRight: 6 }}>
                Pages du rapport Smart_City :
              </span>
              {SMART_CITY_PAGES.map(t => (
                <button
                  key={t.id}
                  className={`btn ${pbiTab === t.id ? 'btn-primary' : 'btn-outline'}`}
                  style={{ padding: '6px 12px', fontSize: 12 }}
                  onClick={() => setPbiTab(t.id)}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {pbiTab !== 'presentation' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Segment capteur_nom :</span>
                <select
                  className="select-sm"
                  value={selectedSensor}
                  onChange={e => handleSelectSensorForForecast(e.target.value)}
                >
                  <option value="ALL">Toutes les stations (34)</option>
                  {stations.map(s => (
                    <option key={s.id} value={s.name}>{s.name}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* PAGE 1 : PRÉSENTATION */}
          {pbiTab === 'presentation' && (
            <div className="charts-grid" style={{ gridTemplateColumns: '1.35fr 1fr' }}>
              <div className="card" style={{ background: 'linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,41,59,0.92))', border: '1px solid var(--border)' }}>
                <h2 style={{ fontSize: 26, fontWeight: 800, marginBottom: 10 }}>
                  <span style={{ color: '#22c55e' }}>Bienvenue </span>
                  <span style={{ color: '#ef4444' }}>dans le rapport </span>
                  <span style={{ color: '#eab308' }}>de Smart City</span>
                </h2>
                <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 18 }}>
                  Dans ce rapport vous trouverez des statistiques et informations temps réel sur la qualité de l'air issues directement de la base PostgreSQL Supabase (<strong>{analytics.totalRows} mesures</strong> sur <strong>34 capteurs</strong>).
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  <div style={{ padding: 12, borderRadius: 8, background: 'rgba(255,255,255,0.03)', borderLeft: '3px solid #0ea5e9' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>1 - Statistiques aqi</strong>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                      Évolutions de l'indice European AQI par mois, par jour et par heure, avec jauge Min / Moyenne / Max et sélection par capteur.
                    </p>
                  </div>
                  <div style={{ padding: 12, borderRadius: 8, background: 'rgba(255,255,255,0.03)', borderLeft: '3px solid #10b981' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>2 - Autres données</strong>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                      Tableau détaillé accompagnant l'AQI : polluants (NO₂, O₃, PM10, PM2.5, SO₂) et paramètres météo (Température, Humidité, Précipitations, Vent, Direction).
                    </p>
                  </div>
                  <div style={{ padding: 12, borderRadius: 8, background: 'rgba(255,255,255,0.03)', borderLeft: '3px solid #eab308' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>3 - Carte & Actualité</strong>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                      Carte interactive en direct montrant la position géographique des 34 capteurs (taille et couleur selon l'AQI) et page Actualité temps réel (dernier relevé, dernier jour, dernière heure).
                    </p>
                  </div>
                  <div style={{ padding: 12, borderRadius: 8, background: 'rgba(255,255,255,0.03)', borderLeft: '3px solid #a855f7' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>4 - Prévisions</strong>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                      Prédictions horaires de l'AQI (`aqi_predit`) pour les 24 prochaines heures générées par le modèle Machine Learning LightGBM.
                    </p>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <h2 className="card-title">Échelle officielle European AQI (Table de référence)</h2>
                </div>
                <div className="sensor-table-wrap">
                  <table className="sensor-table">
                    <thead>
                      <tr>
                        <th>European_AQI_Min</th>
                        <th>European_AQI_Max</th>
                        <th>Couleur</th>
                        <th>Qualité</th>
                      </tr>
                    </thead>
                    <tbody>
                      {EAQI_REF_TABLE.map(r => (
                        <tr key={r.qualite}>
                          <td><strong>{r.min}</strong></td>
                          <td><strong>{r.max}</strong></td>
                          <td>
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                              <span style={{ width: 12, height: 12, borderRadius: '50%', background: r.color, display: 'inline-block' }} />
                              {r.colorName}
                            </span>
                          </td>
                          <td><strong>{r.qualite}</strong></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* PAGE 2 : STATISTIQUES AQI */}
          {pbiTab === 'stats_aqi' && (
            <>
              <div className="charts-grid" style={{ gridTemplateColumns: '1fr 1.2fr 1.2fr' }}>
                <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <div className="card-header" style={{ width: '100%' }}>
                    <h2 className="card-title">Jauge European AQI ({selectedSensor === 'ALL' ? 'Toutes stations' : selectedSensor})</h2>
                  </div>
                  <AqiGauge aqi={Math.round(selectedSensor === 'ALL' ? analytics.aqiMean : (selectedStationObj?.aqiMean || analytics.aqiMean))} />
                  <div style={{ display: 'flex', justifyContent: 'space-around', width: '100%', marginTop: 12, fontSize: 12, color: 'var(--text-secondary)' }}>
                    <span>Min : <strong>{selectedSensor === 'ALL' ? analytics.aqiMin : selectedStationObj?.aqiMin}</strong></span>
                    <span>Moyenne : <strong>{selectedSensor === 'ALL' ? analytics.aqiMean : selectedStationObj?.aqiMean}</strong></span>
                    <span>Max : <strong>{selectedSensor === 'ALL' ? analytics.aqiMax : selectedStationObj?.aqiMax}</strong></span>
                  </div>
                </div>

                <div className="card chart-card">
                  <div className="card-header">
                    <h2 className="card-title">Moyenne de european_aqi par Jour</h2>
                  </div>
                  <ResponsiveContainer width="100%" height={240}>
                    <LineChart data={analytics.dailySeries || []}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                      <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                      <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)', borderRadius: 8 }} />
                      <Legend wrapperStyle={{ fontSize: 12 }} />
                      <Line type="monotone" dataKey="aqiMean" name="Moyenne de european_aqi" stroke="#0ea5e9" strokeWidth={2.5} dot={{ r: 3 }} />
                      <Line type="monotone" dataKey="aqiMax" name="Max de european_aqi" stroke="#ef4444" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="card chart-card">
                  <div className="card-header">
                    <h2 className="card-title">Moyenne de european_aqi par Heure (00h → 23h)</h2>
                  </div>
                  <ResponsiveContainer width="100%" height={240}>
                    <AreaChart data={analytics.hourlyProfile || []}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="hour" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                      <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                      <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)', borderRadius: 8 }} />
                      <Legend wrapperStyle={{ fontSize: 12 }} />
                      <Area type="monotone" dataKey="aqi" name="Moyenne de european_aqi" stroke="#a855f7" fill="rgba(168,85,247,0.25)" strokeWidth={2.5} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}

          {/* PAGE 3 : AUTRES DONNÉES */}
          {pbiTab === 'autres' && (
            <div className="card">
              <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
                <h2 className="card-title">
                  Table « autres données » — Qualité de l'air & Météo ({filteredRawRows.length} relevés affichés)
                </h2>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  Colonnes identiques au visuel Power BI : capteur_nom, time, latitude, longitude, NO₂, O₃, PM10, PM2.5, Précip., Humidité, SO₂, Temp., Dir. Vent, Vit. Vent
                </span>
              </div>
              <div className="sensor-table-wrap" style={{ maxHeight: 540, overflowY: 'auto' }}>
                <table className="sensor-table">
                  <thead>
                    <tr>
                      <th>capteur_nom</th>
                      <th>time</th>
                      <th>lat / lon</th>
                      <th>NO₂</th>
                      <th>Ozone (O₃)</th>
                      <th>PM10</th>
                      <th>PM2.5</th>
                      <th>SO₂</th>
                      <th>Précip.</th>
                      <th>Humidité</th>
                      <th>Temp (°C)</th>
                      <th>Dir. Vent</th>
                      <th>Vit. Vent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRawRows.map((r, i) => (
                      <tr key={`${r.capteur_id}-${r.time}-${i}`}>
                        <td><strong>{r.capteur_nom}</strong></td>
                        <td style={{ whiteSpace: 'nowrap', fontSize: 12 }}>{r.timeFormatted}</td>
                        <td style={{ fontSize: 11, color: 'var(--text-muted)' }}>{r.latitude}, {r.longitude}</td>
                        <td>{r.nitrogen_dioxide ?? '—'}</td>
                        <td>{r.ozone ?? '—'}</td>
                        <td>{r.pm10 ?? '—'}</td>
                        <td><strong>{r.pm2_5 ?? '—'}</strong></td>
                        <td>{r.sulphur_dioxide ?? '—'}</td>
                        <td>{r.precipitation ?? 0} mm</td>
                        <td>{r.relative_humidity_2m ?? '—'} %</td>
                        <td>{r.temperature_2m ?? '—'} °C</td>
                        <td>{r.wind_direction_10m ?? '—'}°</td>
                        <td>{r.wind_speed_10m ?? '—'} km/h</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* PAGE 4 : CARTE */}
          {pbiTab === 'carte' && (
            <div className="charts-grid" style={{ gridTemplateColumns: '300px 1fr' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div className="card" style={{ textAlign: 'center', padding: '20px 16px' }}>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Moyenne de european_aqi
                  </div>
                  <div style={{ fontSize: 44, fontWeight: 800, color: getAqiLevel(selectedSensor === 'ALL' ? analytics.aqiMean : selectedStationObj?.aqiMean).color, margin: '8px 0' }}>
                    {selectedSensor === 'ALL' ? analytics.aqiMean : selectedStationObj?.aqiMean}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    {selectedSensor === 'ALL' ? 'Moyenne régionale (34 capteurs)' : selectedStationObj?.name}
                  </div>
                </div>
                <div className="card" style={{ flex: 1, maxHeight: 420, overflowY: 'auto' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 8, color: 'var(--text-secondary)' }}>
                    Sélection rapide capteur_nom :
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <button
                      className={`btn ${selectedSensor === 'ALL' ? 'btn-primary' : 'btn-outline'}`}
                      style={{ justifyContent: 'flex-start', padding: '5px 10px', fontSize: 12 }}
                      onClick={() => setSelectedSensor('ALL')}
                    >
                      Toutes les stations (34)
                    </button>
                    {stations.map(s => (
                      <button
                        key={s.id}
                        className={`btn ${selectedSensor === s.name ? 'btn-primary' : 'btn-outline'}`}
                        style={{ justifyContent: 'space-between', padding: '5px 10px', fontSize: 12 }}
                        onClick={() => setSelectedSensor(s.name)}
                      >
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.name}</span>
                        <span style={{ color: getAqiLevel(s.aqiMean).color, fontWeight: 700 }}>{s.aqiMean}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="card" style={{ padding: 0, overflow: 'hidden', minHeight: 540 }}>
                <MapContainer center={[48.8566, 2.3522]} zoom={10} style={{ height: 540, width: '100%' }}>
                  <TileLayer
                    attribution='&copy; OpenStreetMap'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  />
                  {stations
                    .filter(s => selectedSensor === 'ALL' || s.name === selectedSensor)
                    .filter(s => s.lat && s.lng)
                    .map(s => {
                      const lvl = getAqiLevel(s.aqiMean);
                      return (
                        <CircleMarker
                          key={s.id}
                          center={[s.lat, s.lng]}
                          radius={Math.max(8, Math.min(24, (s.aqiMean || 20) * 0.45))}
                          pathOptions={{ color: lvl.color, fillColor: lvl.color, fillOpacity: 0.78, weight: 2 }}
                        >
                          <Popup>
                            <div style={{ minWidth: 190 }}>
                              <strong>{s.name}</strong> ({s.id})
                              <hr style={{ margin: '6px 0', opacity: 0.2 }} />
                              <div>Moyenne de european_aqi : <strong>{s.aqiMean}</strong></div>
                              <div>Pic european_aqi : <strong>{s.aqiMax}</strong></div>
                              <div>Moyenne de precipitation : <strong>{s.precipMean} mm</strong></div>
                              <div>Moyenne de wind_speed_10m : <strong>{s.windMean} km/h</strong></div>
                              <div>Moyenne de wind_direction_10m : <strong>{s.windDirMean}°</strong></div>
                            </div>
                          </Popup>
                        </CircleMarker>
                      );
                    })}
                </MapContainer>
              </div>
            </div>
          )}

          {/* PAGE 5 : ACTUALITÉ */}
          {pbiTab === 'actualite' && selectedStationObj && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div className="charts-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
                  <div className="card-header" style={{ width: '100%' }}>
                    <h2 className="card-title">Jauge Temps Réel — Dernier relevé European AQI</h2>
                  </div>
                  <AqiGauge aqi={Math.round(selectedStationObj.aqiLast || selectedStationObj.aqiMean)} />
                  <div style={{ display: 'flex', gap: 24, marginTop: 12, fontSize: 13 }}>
                    <span>Min de european_aqi : <strong>{selectedStationObj.aqiMin}</strong></span>
                    <span>Max de european_aqi : <strong>{selectedStationObj.aqiMax}</strong></span>
                  </div>
                </div>

                <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 16, padding: 28 }}>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Dernier capteur_nom & capteur_id
                  </div>
                  <div style={{ fontSize: 30, fontWeight: 800, color: 'var(--primary)' }}>
                    {selectedStationObj.name}
                  </div>
                  <div style={{ fontSize: 15, color: 'var(--text-secondary)' }}>
                    Identifiant station (`capteur_id`) : <code>{selectedStationObj.id}</code>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginTop: 8 }}>
                    <div style={{ padding: 16, borderRadius: 10, background: 'var(--bg-main)', border: '1px solid var(--border)' }}>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>DernierJour</div>
                      <div style={{ fontSize: 22, fontWeight: 800, marginTop: 4 }}>{selectedStationObj.lastDay}</div>
                    </div>
                    <div style={{ padding: 16, borderRadius: 10, background: 'var(--bg-main)', border: '1px solid var(--border)' }}>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>derniereheure</div>
                      <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--secondary)', marginTop: 4 }}>{selectedStationObj.lastHour}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* PAGE 6 : PRÉVISIONS */}
          {pbiTab === 'previsions' && (
            <div className="charts-grid" style={{ gridTemplateColumns: '320px 1fr' }}>
              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 8 }}>
                    Segment Heure (Horizon de prédiction : 1h → {maxHorizon}h)
                  </div>
                  <input
                    type="range"
                    min={4}
                    max={24}
                    value={maxHorizon}
                    onChange={e => setMaxHorizon(+e.target.value)}
                    style={{ width: '100%' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)' }}>
                    <span>+1h</span>
                    <span>+{maxHorizon}h</span>
                    <span>+24h</span>
                  </div>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  Ce visuel reproduit la page <strong>prévisions</strong> de <code>Smart_City.pbix</code> : évolution de <strong>Moyenne de aqi_predit</strong> par <strong>Heure</strong> (+1h à +24h) issue du bundle de 24 modèles <code>LGBMRegressor</code>.
                </div>
              </div>

              <div className="card chart-card">
                <div className="card-header">
                  <h2 className="card-title">Moyenne de aqi_predit par Heure (+1h à +{maxHorizon}h)</h2>
                </div>
                <ResponsiveContainer width="100%" height={340}>
                  <LineChart data={forecastSeries}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="hour" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                    <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                    <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)', borderRadius: 8 }} />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                    <Line
                      type="monotone"
                      dataKey="aqi"
                      name="Moyenne de aqi_predit (EAQI)"
                      stroke="#10b981"
                      strokeWidth={3}
                      dot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════
          MODE 2 : POWER BI SERVICE CLOUD + CERTIFICAT SSL PASSERELLE
         ═══════════════════════════════════════════════════════════════════════ */}
      {mode === 'embed' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Bandeau Certificat SSL Passerelle (Back/prod-ca-2021.crt) */}
          <div className="card" style={{ padding: '14px 18px', borderLeft: '4px solid var(--primary)', display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
              <div>
                <h3 style={{ fontSize: 15, fontWeight: 700, margin: 0 }}>
                  🔐 Certificat SSL Supabase (<code>Back/prod-ca-2021.crt</code>) pour la Passerelle Power BI
                </h3>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                  Le pooler Supabase (<code>aws-0-eu-west-2.pooler.supabase.com</code>) exige une connexion TLS signée par <strong>Supabase Root 2021 CA</strong>. Pour que la passerelle locale (On-Premises Data Gateway) ou Power BI Desktop valide le certificat SSL :
                </p>
              </div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <button className="btn btn-primary" style={{ fontSize: 12, padding: '6px 12px' }} onClick={handleInstallSslCert}>
                  🛡️ Installer prod-ca-2021.crt dans Windows (1 clic)
                </button>
                <a
                  href="http://localhost:8080/api/powerbi/ssl-cert"
                  download="prod-ca-2021.crt"
                  className="btn btn-outline"
                  style={{ fontSize: 12, padding: '6px 12px' }}
                >
                  ⬇ Télécharger prod-ca-2021.crt
                </a>
                <button className="btn btn-outline" style={{ fontSize: 12, padding: '6px 12px' }} onClick={handleConnectPostgres}>
                  🔄 Tester la connexion Cloud
                </button>
              </div>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', background: 'var(--bg-main)', padding: '10px 14px', borderRadius: 8 }}>
              <strong>Pourquoi décocher SSL dans Supabase ne suffit pas sur Power BI Cloud :</strong> l'hôte <code>aws-0-eu-west-2.pooler.supabase.com</code> est le pooler Supavisor qui impose toujours SSL.
              <br />
              • <strong>Avec Passerelle locale (On-Premises Gateway) :</strong> cliquez sur <em>« Installer prod-ca-2021.crt dans Windows »</em> ci-dessus, puis dans Power BI Service → <em>Paramètres du modèle sémantique Smart_City → Connexions de passerelle</em>, sélectionnez votre passerelle locale avec <em>Chiffrer les connexions</em> activé.
              <br />
              • <strong>Sans passerelle (en 30 secondes depuis Power BI Desktop) :</strong> ouvrez <code>Smart_City.pbix</code> dans Power BI Desktop, passez la table <code>mesures</code> du mode <em>DirectQuery</em> au mode <strong>Importer</strong> (Vue Modèle → Propriétés → Avancé → Mode de stockage : <em>Importer</em>), puis cliquez sur <strong>Publier</strong>.
            </div>
          </div>

          {hasSdkConfig && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {embedConfig.pages?.length > 0 && (
                <div className="card" style={{ padding: '10px 14px', display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)', marginRight: 6 }}>Pages Power BI Service :</span>
                  {embedConfig.pages.map(p => (
                    <button
                      key={p.name}
                      className={`btn ${activePage === p.name ? 'btn-primary' : 'btn-outline'}`}
                      style={{ padding: '5px 12px', fontSize: 12 }}
                      onClick={() => switchPbiPage(p.name)}
                    >
                      {p.displayName}
                    </button>
                  ))}
                </div>
              )}
              <div className="pbi-embed-wrap" style={{ height: 680 }}>
                {embedState === 'loading' && (
                  <div className="pbi-loading">
                    <div className="spinner" />
                    <span>Chargement du rapport Power BI « {embedConfig.reportName || 'Smart_City'} »…</span>
                  </div>
                )}
                <PowerBIEmbed
                  embedConfig={{
                    type: 'report',
                    id: embedConfig.reportId,
                    embedUrl: embedConfig.embedUrl,
                    accessToken: embedConfig.accessToken || embedConfig.token,
                    tokenType: embedConfig.tokenType === 'aad' ? models.TokenType.Aad : models.TokenType.Embed,
                    pageName: activePage || undefined,
                    settings: {
                      panes: { filters: { visible: true, expanded: false }, pageNavigation: { visible: true } },
                      background: models.BackgroundType.Default,
                    },
                  }}
                  eventHandlers={new Map([
                    ['loaded',   () => setEmbedState('loaded')],
                    ['rendered', () => setEmbedState('loaded')],
                    ['error',    (e) => { console.error('PBI Error:', e); setEmbedState('error'); }],
                  ])}
                  cssClassName="pbi-iframe"
                  getEmbeddedComponent={(report) => { window._pbiReport = report; }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════
          MODE 3 : SYNTHÈSE ANALYTIQUE & CORRÉLATIONS
         ═══════════════════════════════════════════════════════════════════════ */}
      {mode === 'live' && analytics && (
        <>
          <div className="charts-grid">
            <div className="card chart-card">
              <div className="card-header">
                <h2 className="card-title">Profil horaire moyen (00h → 23h) — Cycle diurne Trafic & Ozone</h2>
              </div>
              <ResponsiveContainer width="100%" height={280}>
                <ComposedChart data={analytics.hourlyProfile} margin={{ top: 10, right: 15, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="hour" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                  <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)', borderRadius: 8 }} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="no2" name="NO₂ moyen (µg/m³)" fill="#ef4444" opacity={0.75} radius={[3, 3, 0, 0]} />
                  <Line type="monotone" dataKey="o3" name="Ozone O₃ (µg/m³)" stroke="#0ea5e9" strokeWidth={2.5} dot={false} />
                  <Line type="monotone" dataKey="aqi" name="Indice EAQI" stroke="#a855f7" strokeWidth={2.5} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <div className="card chart-card">
              <div className="card-header">
                <h2 className="card-title">Top 10 des stations les plus exposées (EAQI moyen)</h2>
              </div>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={top10Stations} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" width={150} tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)', borderRadius: 8 }} />
                  <Bar dataKey="aqiMean" name="EAQI Moyen" radius={[0, 4, 4, 0]}>
                    {top10Stations.map(s => (
                      <Cell key={s.id} fill={getAqiLevel(s.aqiMean).color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="charts-grid">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Répartition des {analytics.totalRows} mesures par classe EAQI</h2>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {analytics.aqiDistribution.map(b => (
                  <div key={b.label} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ width: 155, fontSize: 13, color: 'var(--text-secondary)' }}>{b.label}</span>
                    <div style={{ flex: 1, height: 12, background: 'var(--bg-main)', borderRadius: 6, overflow: 'hidden' }}>
                      <div style={{ width: `${b.pct}%`, height: '100%', background: b.color }} />
                    </div>
                    <strong style={{ width: 95, textAlign: 'right', fontSize: 13 }}>{b.pct}% ({b.count})</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Corrélations de Pearson (Polluants × Météo)</h2>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
                {analytics.correlations.map(c => {
                  const r = c.r ?? 0;
                  const color = Math.abs(r) > 0.4 ? 'var(--primary)' : 'var(--text-secondary)';
                  return (
                    <div key={c.pair} style={{ padding: 12, borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg-main)' }}>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{c.pair}</div>
                      <div style={{ fontSize: 22, fontWeight: 700, color, marginTop: 4 }}>
                        r = {r > 0 ? `+${r}` : r}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                        {r < -0.2 ? 'Corrélation inverse (dispersion)' : r > 0.2 ? 'Corrélation positive' : 'Faible corrélation'}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
              <h2 className="card-title">Synthèse analytique par station ({stationStats.length} stations)</h2>
              <input
                type="search"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Filtrer une station (ex: Paris, A1, Melun…)"
                style={{ padding: '6px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg-main)', color: 'var(--text-primary)', fontSize: 13 }}
              />
            </div>
            <div className="sensor-table-wrap">
              <table className="sensor-table">
                <thead>
                  <tr>
                    <th>Station</th>
                    <th>Mesures</th>
                    <th>EAQI Moyen</th>
                    <th>EAQI Pic</th>
                    <th>PM2.5 Moy / Max</th>
                    <th>PM10 Moy</th>
                    <th>NO₂ Moy</th>
                    <th>O₃ Moy</th>
                    <th>Temp Moy</th>
                    <th>Vent Moy</th>
                  </tr>
                </thead>
                <tbody>
                  {stationStats.map(s => {
                    const lvl = getAqiLevel(s.aqiMean);
                    return (
                      <tr key={s.id}>
                        <td><strong>{s.name}</strong></td>
                        <td>{s.count}</td>
                        <td><span className={`badge badge-${lvl.badge}`}>{s.aqiMean}</span></td>
                        <td style={{ fontWeight: 600 }}>{s.aqiMax}</td>
                        <td>{s.pm25Mean} / <strong>{s.pm25Max}</strong> µg/m³</td>
                        <td>{s.pm10Mean} µg/m³</td>
                        <td>{s.no2Mean} µg/m³</td>
                        <td>{s.o3Mean} µg/m³</td>
                        <td>{s.tempMean} °C</td>
                        <td>{s.windMean} km/h</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════
          MODE 4 : RAPPORT EDA SWEETVIZ
         ═══════════════════════════════════════════════════════════════════════ */}
      {mode === 'sweetviz' && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <iframe
            title="Rapport Qualité de l'Air Sweetviz d'origine"
            src="http://localhost:8080/api/powerbi/sweetviz"
            style={{ width: '100%', height: 720, border: 'none', borderRadius: 12, background: '#fff' }}
          />
        </div>
      )}
    </div>
  );
}
