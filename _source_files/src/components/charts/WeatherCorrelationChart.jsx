import {
  ComposedChart, Line, Bar, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px' }}>
      <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>{label}</p>
      {payload.map(p => (
        <div key={p.dataKey} style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 12, padding: '2px 0' }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: p.color, flexShrink: 0 }} />
          <span style={{ color: 'var(--text-secondary)' }}>{p.name}</span>
          <span style={{ marginLeft: 'auto', fontWeight: 600, color: 'var(--text-primary)' }}>{p.value}</span>
        </div>
      ))}
    </div>
  );
};

/**
 * Dual-axis chart correlating pollution (line) and weather (bars/area)
 */
export default function WeatherCorrelationChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="timeLabel" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} interval="preserveStartEnd" />
        <YAxis yAxisId="left"  tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }} />

        <Area yAxisId="left" type="monotone" dataKey="humidity" name="Humidité (%)"
          fill="#0ea5e933" stroke="#0ea5e9" strokeWidth={1.5} />
        <Bar yAxisId="right" dataKey="temp" name="Temp (°C)" fill="#f59e0b44" stroke="#f59e0b" strokeWidth={1} />
        <Line yAxisId="left" type="monotone" dataKey="pm25" name="PM2.5 (µg/m³)"
          stroke="#ef4444" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
