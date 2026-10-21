import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import './KpiCard.css';

/**
 * Reusable KPI card with value, unit, trend, and optional sub-value
 */
export default function KpiCard({ title, value, unit, trend, trendLabel, icon: Icon, color = 'var(--primary)', badge, subValue }) {
  const trendIcon =
    trend > 0  ? <ArrowUp  size={14} className="trend-up"   /> :
    trend < 0  ? <ArrowDown size={14} className="trend-down" /> :
                 <Minus     size={14} className="trend-flat" />;

  return (
    <div className="kpi-card card fade-in">
      <div className="kpi-header">
        <span className="kpi-title">{title}</span>
        {Icon && (
          <div className="kpi-icon" style={{ background: `${color}22`, color }}>
            <Icon size={18} />
          </div>
        )}
      </div>

      <div className="kpi-body">
        <div className="kpi-value-row">
          <span className="kpi-value" style={{ color }}>{value ?? '—'}</span>
          {unit && <span className="kpi-unit">{unit}</span>}
        </div>
        {badge && <span className={`badge badge-${badge.type}`}>{badge.label}</span>}
        {subValue && <span className="kpi-sub">{subValue}</span>}
      </div>

      {trend !== undefined && (
        <div className="kpi-trend">
          {trendIcon}
          <span className={trend > 0 ? 'trend-up' : trend < 0 ? 'trend-down' : 'trend-flat'}>
            {Math.abs(trend)}% {trendLabel || 'vs 1h'}
          </span>
        </div>
      )}
    </div>
  );
}
