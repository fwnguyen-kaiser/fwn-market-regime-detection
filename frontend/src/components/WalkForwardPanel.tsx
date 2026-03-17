// src/components/WalkForwardPanel.tsx
import React from 'react';
import type { WalkForwardSummary } from '../types/regime';

interface Props {
  data: WalkForwardSummary | null;
}

export const WalkForwardPanel: React.FC<Props> = ({ data }) => {
  if (!data) {
    return (
      <div className="wf-container">
        <div className="wf-title">WALK-FORWARD VALIDATION</div>
        <div className="wf-empty">Not available</div>
      </div>
    );
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const convergenceRate = ((data.converged_folds / data.n_folds) * 100).toFixed(0);
  const isHealthy = data.converged_folds === data.n_folds;
  const isBicStable = data.std_bic / Math.abs(data.mean_bic) < 0.05; // <5% variation = stable

  return (
    <div className="wf-container">
      <div className="wf-title">WALK-FORWARD VALIDATION</div>

      {/* Top summary row */}
      <div className="wf-summary-row">
        <div className="wf-stat">
          <span className="wf-stat-label">FOLDS</span>
          <span className="wf-stat-value">{data.n_folds}</span>
        </div>
        <div className="wf-stat">
          <span className="wf-stat-label">MEAN BIC</span>
          <span className="wf-stat-value">{data.mean_bic.toFixed(0)}</span>
        </div>
        <div className="wf-stat">
          <span className="wf-stat-label">BIC STD</span>
          <span
            className="wf-stat-value"
            style={{ color: isBicStable ? '#10b981' : '#f59e0b' }}
          >
            ±{data.std_bic.toFixed(0)}
          </span>
        </div>
        <div className="wf-stat">
          <span className="wf-stat-label">AVG SWITCHES</span>
          <span className="wf-stat-value">{data.mean_switches.toFixed(1)}</span>
        </div>
        <div className="wf-stat">
          <span className="wf-stat-label">CONVERGED</span>
          <span
            className="wf-stat-value"
            style={{ color: isHealthy ? '#10b981' : '#ef4444' }}
          >
            {data.converged_folds}/{data.n_folds}
          </span>
        </div>
      </div>

      {/* Per-fold table */}
      <div className="wf-table-wrapper">
        <table className="wf-table">
          <thead>
            <tr>
              <th>FOLD</th>
              <th>TEST RANGE</th>
              <th>BIC</th>
              <th>SWITCHES</th>
              <th>REGIMES</th>
              <th>OK</th>
            </tr>
          </thead>
          <tbody>
            {data.fold_results.map((fold) => (
              <tr key={fold.fold}>
                <td className="wf-fold-num">#{fold.fold}</td>
                <td className="wf-muted">{fold.test_range[0]}–{fold.test_range[1]}</td>
                <td>{fold.bic.toFixed(0)}</td>
                <td style={{ color: fold.n_switches > 15 ? '#f59e0b' : '#94a3b8' }}>
                  {fold.n_switches}
                </td>
                <td className="wf-regimes">
                  {Object.entries(fold.regime_counts).map(([regime, count]) => (
                    <span key={regime} className="wf-regime-badge">
                      {regime.slice(0, 2).toUpperCase()} {count}
                    </span>
                  ))}
                </td>
                <td>
                  <span className={fold.converged ? 'wf-ok' : 'wf-fail'}>
                    {fold.converged ? '✓' : '✗'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};