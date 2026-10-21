import { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getAqiLevel, pm25ToAqi } from '../../utils/airQuality';
import './AirQualityMap.css';

// Fix Leaflet default icon paths
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function MapUpdater({ center }) {
  const map = useMap();
  useEffect(() => { if (center) map.setView(center, map.getZoom()); }, [center, map]);
  return null;
}

export default function AirQualityMap({ sensors = [], center = [48.8566, 2.3522] }) {
  return (
    <div className="map-container">
      <MapContainer center={center} zoom={10} scrollWheelZoom={true} className="leaflet-map">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapUpdater center={center} />

        {sensors.filter(s => s.lat != null && s.lng != null).map(sensor => {
          const aqi   = sensor.aqi != null ? Math.round(sensor.aqi) : pm25ToAqi(sensor.pm25 ?? 0);
          const level = getAqiLevel(aqi);
          return (
            <CircleMarker
              key={sensor.id}
              center={[sensor.lat, sensor.lng]}
              radius={14}
              pathOptions={{
                color: level.color,
                fillColor: level.color,
                fillOpacity: 0.55,
                weight: 2,
              }}
            >
              <Popup>
                <div className="map-popup">
                  <div className="popup-header">
                    <strong>{sensor.name}</strong>
                    <span className={`badge badge-${level.badge}`}>{level.label}</span>
                  </div>
                  <div className="popup-grid">
                    <div className="popup-stat"><span>AQI</span><strong style={{ color: level.color }}>{aqi}</strong></div>
                    <div className="popup-stat"><span>PM2.5</span><strong>{sensor.pm25} µg/m³</strong></div>
                    <div className="popup-stat"><span>PM10</span><strong>{sensor.pm10} µg/m³</strong></div>
                    <div className="popup-stat"><span>NO₂</span><strong>{sensor.no2} µg/m³</strong></div>
                    <div className="popup-stat"><span>Temp</span><strong>{sensor.temp}°C</strong></div>
                    <div className="popup-stat"><span>Humidité</span><strong>{sensor.humidity}%</strong></div>
                  </div>
                  <div className="popup-recommendation">{level.recommendation}</div>
                  <div className="popup-status">
                    <span className={`status-dot ${sensor.status}`} />
                    {sensor.status === 'online' ? 'En ligne' : 'Hors ligne'}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Legend */}
      <div className="map-legend">
        <div className="legend-title">Qualité de l'air</div>
        {[
          { label: 'Bon',      color: '#22c55e' },
          { label: 'Modéré',   color: '#f59e0b' },
          { label: 'Mauvais',  color: '#ef4444' },
          { label: 'Très mauvais', color: '#a855f7' },
        ].map(l => (
          <div key={l.label} className="legend-item">
            <span className="legend-dot" style={{ background: l.color }} />
            <span>{l.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
