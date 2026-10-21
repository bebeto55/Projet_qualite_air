import { getAqiLevel } from '../../utils/airQuality';
import './AqiGauge.css';

/**
 * Semicircular AQI gauge with color zones
 */
export default function AqiGauge({ aqi = 0, size = 200 }) {
  const level  = getAqiLevel(aqi);
  const pct    = Math.min(aqi / 300, 1); // 0→1 over 0–300 range
  const angle  = pct * 180;              // 0°→180° sweep (semicircle)

  const r  = size / 2 - 16;
  const cx = size / 2;
  const cy = size / 2;

  // Polar → cartesian for needle tip
  const rad = ((180 - angle) * Math.PI) / 180;
  const nx  = cx + r * Math.cos(rad);
  const ny  = cy - r * Math.sin(rad);

  // AQI colour zones: good, moderate, usg, unhealthy, very unhealthy
  const zones = [
    { color: '#22c55e', from: 180, to: 144 },
    { color: '#f59e0b', from: 144, to: 108 },
    { color: '#f97316', from: 108, to: 72  },
    { color: '#ef4444', from: 72,  to: 36  },
    { color: '#a855f7', from: 36,  to: 0   },
  ];

  function arcPath(fromDeg, toDeg, r) {
    const f = (fromDeg * Math.PI) / 180;
    const t = (toDeg   * Math.PI) / 180;
    const x1 = cx + r * Math.cos(f);
    const y1 = cy - r * Math.sin(f);
    const x2 = cx + r * Math.cos(t);
    const y2 = cy - r * Math.sin(t);
    const large = Math.abs(fromDeg - toDeg) > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 0 ${x2} ${y2}`;
  }

  return (
    <div className="aqi-gauge-wrap">
      <svg width={size} height={size / 2 + 24} viewBox={`0 0 ${size} ${size / 2 + 24}`}>
        {/* Background track */}
        <path d={arcPath(180, 0, r)} fill="none" stroke="var(--border)" strokeWidth={14} strokeLinecap="round" />

        {/* Coloured zones */}
        {zones.map((z, i) => (
          <path key={i} d={arcPath(z.from, z.to, r)} fill="none" stroke={z.color} strokeWidth={10} opacity={0.35} />
        ))}

        {/* Active arc */}
        <path d={arcPath(180, 180 - angle, r)} fill="none" stroke={level.color} strokeWidth={10} strokeLinecap="round" />

        {/* Needle */}
        <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={level.color} strokeWidth={3} strokeLinecap="round" />
        <circle cx={cx} cy={cy} r={6} fill={level.color} />

        {/* AQI value */}
        <text x={cx} y={cy / 2 + 20} textAnchor="middle" fill={level.color} fontSize={28} fontWeight={700}>{aqi}</text>
        <text x={cx} y={cy / 2 + 38} textAnchor="middle" fill="var(--text-muted)" fontSize={11}>{level.label}</text>
      </svg>
      <div className="aqi-gauge-label">Indice de Qualité de l'Air</div>
    </div>
  );
}
