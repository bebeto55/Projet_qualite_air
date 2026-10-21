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
  const row = payload[0]?.payload;
  return (
    <div className="pred-tooltip">
      <p className="pred-tooltip-date">{label}</p>
      {pred && (
        <div className="pred-tooltip-row">
          <span>{pred.name}</span>
          <span style={{ color: pred.color, fontWeight: 600 }}>{pred.value}</span>
        </div>
      )}
      {row?.lower != null && (
        <div className="pred-tooltip-row">
          <span>Intervalle 80 %</span>
          <span>{row.lower} – {row.upper}</span>
        </div>
      )}
      {row?.confidence != null && (
        <div className="pred-tooltip-row">
          <span>Fiabilité</span>
          <span>{row.confidence}%</span>
        </div>
      )}
      {level && <div className={`pred-tooltip-level badge badge-${level.badge}`}>{level.label}</div>}
    </div>
  );
};

export default function PredictionChart({ data = [] }) {
  // Recharts range area needs [lower, upper] tuples
  const chartData = data.map(d => ({ ...d, band: d.lower != null ? [d.lower, d.upper] : undefined }));
  const hasBand = chartData.some(d => d.band);

  return (
    <div className="prediction-chart">
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="dateLabel" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} interval={2} />
          <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} domain={[0, 'auto']} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }} />

          {hasBand && (
            <Area type="monotone" dataKey="band" name="Intervalle de confiance 80 %"
              stroke="none" fill="#a855f733" />
          )}

          <ReferenceLine y={60} stroke="#f9731688" strokeDasharray="4 4"
            label={{ value: 'Seuil « médiocre »', position: 'insideTopRight', fill: '#f97316', fontSize: 10 }} />

          <Line type="monotone" dataKey="predicted" name="Indice EAQI prédit"
            stroke="#a855f7" strokeWidth={2.5} dot={{ fill: '#a855f7', r: 3 }}
            activeDot={{ r: 6 }} />
        </ComposedChart>
      </ResponsiveContainer>

      {data.some(d => d.confidence != null) && (
        <div className="confidence-row">
          {data.filter((_, i) => i % 4 === 3).map(d => (
            <div key={d.date} className="conf-badge" title={`Fiabilité : ${d.confidence}%`}>
              <span className="conf-label">+{d.h}h</span>
              <div className="conf-bar">
                <div className="conf-fill" style={{ width: `${d.confidence}%`, background: d.confidence > 80 ? 'var(--secondary)' : d.confidence > 60 ? 'var(--warning)' : 'var(--danger)' }} />
              </div>
              <span className="conf-pct">{d.confidence}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
