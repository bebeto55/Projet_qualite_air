import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { getAqiLevel } from '../../utils/airQuality';
import './PredictionChart.css';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const pred = payload.find(p => p.dataKey === 'predicted');
  const level = pred ? getAqiLevel(pred.value) : null;
  return (
    <div className="pred-tooltip">
      <p className="pred-tooltip-date">{label}</p>
      {payload.map(p => (
        <div key={p.dataKey} className="pred-tooltip-row">
          <span>{p.name}</span>
          <span style={{ color: p.color, fontWeight: 600 }}>{p.value} µg/m³</span>
        </div>
      ))}
      {level && <div className={`pred-tooltip-level badge badge-${level.badge}`}>{level.label}</div>}
    </div>
  );
};

export default function PredictionChart({ data = [] }) {
  return (
    <div className="prediction-chart">
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="dateLabel" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
          <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }} />

          {/* Confidence interval shaded area */}
          <Area type="monotone" dataKey="upper" name="Borne supérieure"
            stroke="none" fill="#a855f722" legendType="none" />
          <Area type="monotone" dataKey="lower" name="Borne inférieure"
            stroke="none" fill="#0f172a" legendType="none" />

          {/* Threshold */}
          <ReferenceLine y={50} stroke="#ef444488" strokeDasharray="4 4"
            label={{ value: 'Seuil PM2.5', position: 'insideTopRight', fill: '#ef4444', fontSize: 10 }} />

          {/* Predicted line */}
          <Line type="monotone" dataKey="predicted" name="PM2.5 prédit (µg/m³)"
            stroke="#a855f7" strokeWidth={2.5} dot={{ fill: '#a855f7', r: 4 }}
            activeDot={{ r: 6 }} />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Confidence badges */}
      <div className="confidence-row">
        {data.map(d => (
          <div key={d.date} className="conf-badge" title={`Confiance: ${d.confidence}%`}>
            <span className="conf-label">{d.dateLabel?.split(' ').slice(0,2).join(' ')}</span>
            <div className="conf-bar">
              <div className="conf-fill" style={{ width: `${d.confidence}%`, background: d.confidence > 80 ? 'var(--secondary)' : d.confidence > 60 ? 'var(--warning)' : 'var(--danger)' }} />
            </div>
            <span className="conf-pct">{d.confidence}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
