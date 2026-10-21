import { useState } from 'react';
import { Report } from 'powerbi-client';
import { PowerBIEmbed } from 'powerbi-client-react';
import { models } from 'powerbi-client';
import './PowerBIPanel.css';

/**
 * Power BI embed panel.
 * Requires VITE_POWERBI_EMBED_URL, VITE_POWERBI_REPORT_ID, VITE_POWERBI_ACCESS_TOKEN
 * env variables (or fetched dynamically from the backend).
 *
 * Without those vars, shows a placeholder/setup guide.
 */
export default function PowerBIPanel({ embedConfig }) {
  const [embedState, setEmbedState] = useState('idle');
  const hasConfig = embedConfig?.embedUrl && embedConfig?.accessToken && embedConfig?.reportId;

  if (!hasConfig) {
    return (
      <div className="pbi-placeholder">
        <div className="pbi-icon">📊</div>
        <h3>Intégration Power BI</h3>
        <p>Configurez les variables d'environnement pour afficher le rapport Power BI intégré.</p>
        <div className="pbi-setup-steps">
          <h4>Configuration requise :</h4>
          <ol>
            <li>Publiez votre rapport dans Power BI Service</li>
            <li>Activez l'intégration «&nbsp;Embed for your organization&nbsp;»</li>
            <li>
              Ajoutez ces variables dans <code>.env</code> :
              <pre>{`VITE_POWERBI_REPORT_ID=<votre-report-id>
VITE_POWERBI_EMBED_URL=https://app.powerbi.com/reportEmbed?reportId=...
VITE_POWERBI_ACCESS_TOKEN=<token-aad-ou-embed>`}</pre>
            </li>
            <li>Ou configurez l'endpoint backend <code>/api/powerbi/embed-config</code></li>
          </ol>
        </div>
        <a
          href="https://learn.microsoft.com/fr-fr/power-bi/developer/embedded/embed-sample-for-your-organization"
          target="_blank" rel="noopener noreferrer"
          className="btn btn-primary pbi-docs-link"
        >
          Documentation officielle →
        </a>
      </div>
    );
  }

  return (
    <div className="pbi-embed-wrap">
      {embedState === 'loading' && (
        <div className="pbi-loading">
          <div className="spinner" />
          <span>Chargement du rapport Power BI…</span>
        </div>
      )}
      <PowerBIEmbed
        embedConfig={{
          type: 'report',
          id: embedConfig.reportId,
          embedUrl: embedConfig.embedUrl,
          accessToken: embedConfig.accessToken,
          tokenType: models.TokenType.Embed,
          settings: {
            panes: { filters: { visible: false }, pageNavigation: { visible: true } },
            background: models.BackgroundType.Transparent,
          },
        }}
        eventHandlers={new Map([
          ['loaded',  () => setEmbedState('loaded')],
          ['error',   (e) => { console.error('PBI Error:', e); setEmbedState('error'); }],
        ])}
        cssClassName="pbi-iframe"
        getEmbeddedComponent={(report) => { window._pbiReport = report; }}
      />
      {embedState === 'error' && (
        <div className="pbi-error">Erreur de chargement du rapport Power BI. Vérifiez le token et l'URL d'embed.</div>
      )}
    </div>
  );
}
