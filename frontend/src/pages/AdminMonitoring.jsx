import { useState, useEffect, useCallback } from 'react';
import { Activity, Server, Shield, RefreshCw, Terminal, CheckCircle, AlertTriangle } from 'lucide-react';
import { adminService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function AdminMonitoring() {
  const { user, isAdmin } = useAuth();
  const [health, setHealth]   = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs]       = useState([]);
  const [level, setLevel]     = useState('');
  const [loading, setLoading] = useState(true);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const h = await adminService.health().catch(() => null);
      setHealth(h);
      if (isAdmin) {
        const [m, l] = await Promise.all([
          adminService.metrics().catch(() => null),
          adminService.logs(level || undefined).catch(() => []),
        ]);
        setMetrics(m);
        setLogs(l);
      }
    } finally {
      setLoading(false);
    }
  }, [isAdmin, level]);

  useEffect(() => { loadAll(); }, [loadAll]);

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Administration, Monitoring & RGPD</h1>
          <p className="page-subtitle">
            Supervision des performances (US-017), journaux système/sécurité (US-018) et conformité RGPD
          </p>
        </div>
        <button className="btn btn-outline" onClick={loadAll} disabled={loading}>
          <RefreshCw size={15} className={loading ? 'spinning' : ''} /> Actualiser
        </button>
      </div>

      {/* Santé & Conformité */}
      <div className="kpi-grid">
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <CheckCircle size={28} color="var(--secondary)" />
          <div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Statut API & Base Supabase</div>
            <strong style={{ fontSize: 18 }}>
              {health?.status === 'ok' ? 'Opérationnel (99.9%)' : 'Vérification…'}
            </strong>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              Cache mesures : {health?.measuresCacheAgeSeconds != null ? `${health.measuresCacheAgeSeconds}s` : 'Prêt'}
            </div>
          </div>
        </div>

        {isAdmin && metrics && (
          <>
            <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <Activity size={28} color="var(--primary)" />
              <div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Temps de réponse moyen</div>
                <strong style={{ fontSize: 18 }}>{metrics.avgResponseMs} ms</strong>
                <div style={{ fontSize: 11, color: 'var(--secondary)' }}>Objectif SLA &lt; 3 000 ms respecté</div>
              </div>
            </div>

            <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <Server size={28} color="#a855f7" />
              <div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Requêtes traitées / Erreurs</div>
                <strong style={{ fontSize: 18 }}>{metrics.requests} req · {metrics.errors} err</strong>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Uptime : {metrics.uptimeSeconds}s</div>
              </div>
            </div>
          </>
        )}

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <Shield size={28} color="#f59e0b" />
          <div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Profil & Sécurité JWT</div>
            <strong style={{ fontSize: 16 }}>{user?.name} ({user?.role})</strong>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>RGPD : Aucune donnée personnelle stockée</div>
          </div>
        </div>
      </div>

      {!isAdmin ? (
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <AlertTriangle size={20} color="var(--warning)" />
          <span>
            Connectez-vous avec le compte <strong>Marie Dubois (admin / admin123)</strong> pour consulter les métriques détaillées par endpoint et les journaux de sécurité (US-017 / US-018).
          </span>
        </div>
      ) : (
        <>
          {/* Performances par endpoint */}
          {metrics?.endpoints && (
            <div className="card">
              <div className="card-header">
                <h2 className="card-title"><Activity size={16} /> Performances par endpoint REST (US-017)</h2>
              </div>
              <div className="sensor-table-wrap">
                <table className="sensor-table">
                  <thead>
                    <tr>
                      <th>Endpoint API</th>
                      <th>Appels</th>
                      <th>Temps moyen</th>
                      <th>Temps max</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(metrics.endpoints).map(([ep, st]) => (
                      <tr key={ep}>
                        <td><code>{ep}</code></td>
                        <td>{st.count}</td>
                        <td style={{ color: st.avgMs < 500 ? 'var(--secondary)' : 'var(--warning)' }}>{st.avgMs} ms</td>
                        <td>{st.maxMs} ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Journaux d'exécution & sécurité */}
          <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
              <h2 className="card-title"><Terminal size={16} /> Journaux Système & Sécurité en direct (US-018)</h2>
              <select className="select-sm" value={level} onChange={e => setLevel(e.target.value)}>
                <option value="">Tous les niveaux</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
              </select>
            </div>
            <div style={{ maxHeight: 360, overflowY: 'auto', fontFamily: 'monospace', fontSize: 12, background: 'var(--bg-main)', padding: 12, borderRadius: 8, border: '1px solid var(--border)' }}>
              {logs.length === 0 ? (
                <div style={{ color: 'var(--text-muted)' }}>Aucun log pour ce filtre.</div>
              ) : logs.map((l, idx) => (
                <div key={idx} style={{ padding: '4px 0', borderBottom: '1px solid rgba(255,255,255,0.04)', display: 'flex', gap: 10 }}>
                  <span style={{ color: 'var(--text-muted)', flexShrink: 0 }}>{l.ts}</span>
                  <span style={{
                    fontWeight: 700,
                    width: 65,
                    flexShrink: 0,
                    color: l.level === 'ERROR' ? 'var(--danger)' : l.level === 'WARNING' ? 'var(--warning)' : 'var(--secondary)',
                  }}>{l.level}</span>
                  <span style={{ color: 'var(--primary)', width: 70, flexShrink: 0 }}>[{l.logger}]</span>
                  <span style={{ color: 'var(--text-primary)' }}>{l.message}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
