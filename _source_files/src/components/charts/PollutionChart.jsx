import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { useState } from 'react';
import { THRESHOLDS } from '../../utils/airQuality';
import './PollutionChart.css';

const POLLUTANTS = [
  { key: 'pm25', label: 'PM2.5', color: '#ef4444' },
  { key: 'pm10', label: 'PM10',  color: '#f97316' },
  { key: 'no2',  label: 'NO₂',   color: '#a855f7' },
  { key: 'o3',   label: 'O₃',    color: '#0ea5e9' },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="tooltip-time">{label}</p>
      {payload.map(p => (
        <div key={p.dataKey} className="tooltip-row">
          <span className="tooltip-dot" style={{ background: p.color }} />
          <span>{p.name}</span>
          <span className="tooltip-val">{p.value} µg/m³</span>
        </div>
      ))}
    </div>
  );
};

export default function PollutionChart({ data = [], type = 'line' }) {
  const [active, setActive] = useState({ pm25: true, pm10: true, no2: false, o3: false });

  const toggle = (key) => setActive(prev => ({ ...prev, [key]: !prev[key] }));

  const ChartComponent = type === 'area' ? AreaChart : LineChart;

  return (
    <div className="pollution-chart">
      {/* Pollutant toggles */}
      <div className="chart-toggles">
        {POLLUTANTS.map(p => (
          <button
            key={p.key}
            className={`toggle-btn ${active[p.key] ? 'on' : ''}`}
            style={{ '--c': p.color }}
            onClick={() => toggle(p.key)}
          >
            <span className="toggle-dot" />
            {p.label}
          </button>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <ChartComponent data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="timeLabel" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />

          {/* Threshold reference line for PM2.5 */}
          {active.pm25 && (
            <ReferenceLine y={THRESHOLDS.pm25.bad} stroke="#ef4444" strokeDasharray="4 4"
              label={{ value: 'Seuil', position: 'insideTopRight', fill: '#ef4444', fontSize: 10 }} />
          )}

          {POLLUTANTS.map(p =>
            active[p.key] && (
              type === 'area'
                ? <Area key={p.key} type="monotone" dataKey={p.key} name={p.label}
                    stroke={p.color} fill={`${p.color}22`} strokeWidth={2} dot={false} />
                : <Line key={p.key} type="monotone" dataKey={p.key} name={p.label}
                    stroke={p.color} strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
            )
          )}
        </ChartComponent>
      </ResponsiveContainer>
    </div>
  );
}
