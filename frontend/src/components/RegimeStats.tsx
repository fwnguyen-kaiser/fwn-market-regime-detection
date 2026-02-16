import React from 'react';
import type { AnalysisResult } from '../types/regime';

// --- HELPER FUNCTIONS (Dùng chung) ---
const getRegimeColor = (regime: string) => {
  if (regime.includes('Bull')) return '#10b981';     // Xanh
  if (regime.includes('Bear')) return '#ef4444';     // Đỏ
  if (regime.includes('Sideways') || regime.includes('High')) return '#f59e0b'; // Vàng/Cam
  return '#8b5cf6'; // Tím mặc định
};

interface Props {
  result: AnalysisResult;
}

// ------------------------------------------------------------------
// 1. CURRENT STATUS COMPONENT (Hàng 1 - Cột 3)
// ------------------------------------------------------------------
export const CurrentStatus: React.FC<Props> = ({ result }) => {
  return (
    <div className="current-regime-banner">
      <div className="banner-content">
        <div className="banner-label">CURRENT MARKET STATUS</div>
        <div 
          className="banner-value" 
          style={{ color: getRegimeColor(result.current_regime) }}
        >
          {result.current_regime}
        </div>
        <div className="banner-subtext">
          Engineered from {result.total_days} observations • {result.n_states}-state Latent Model
        </div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------
// 2. TRIPLE STATS COMPONENT (Hàng 2 - Cột 3)
// ------------------------------------------------------------------
export const TripleStats: React.FC<Props> = ({ result }) => {
  const getQualityTheme = (quality: string) => {
    const q = quality.toUpperCase();
    if (q.includes('GOOD')) return { color: '#10b981', text: 'GOOD' };
    if (q.includes('MODERATE')) return { color: '#f59e0b', text: 'MODERATE' };
    return { color: '#ef4444', text: 'POOR' };
  };

  const quality = getQualityTheme(result.persistence.quality);

  return (
    <div className="stats-grid">
      {/* Persistence Score */}
      <div className="stat-card">
        <div className="stat-card-label">PERSISTENCE SCORE</div>
        <div className="stat-card-value">
          {(result.persistence.persistence_score * 100).toFixed(1)}%
        </div>
      </div>

      {/* Avg Duration */}
      <div className="stat-card">
        <div className="stat-card-label">AVG REGIME LIFE</div>
        <div className="stat-card-value">
          {result.persistence.avg_duration.toFixed(1)}
          <span className="stat-unit">days</span>
        </div>
      </div>

      {/* Model Quality */}
      <div className="stat-card">
        <div className="stat-card-label">MODEL QUALITY</div>
        <div className="stat-card-value" style={{ color: quality.color }}>
          {quality.text}
        </div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------
// 3. STABILITY METRICS COMPONENT (Hàng 3 - Cột 2 & 3)
// ------------------------------------------------------------------
export const StabilityMetrics: React.FC<Props> = ({ result }) => {
  return (
    <div className="persistence-list-container">
      <div className="probability-title">Regime Stability Metrics</div>
      
      <div className="stability-scroll-area">
        {Object.entries(result.persistence.duration_by_regime)
          .sort((a, b) => b[1].avg - a[1].avg) // Sắp xếp theo độ bền giảm dần
          .map(([regime, stats]) => (
            <div key={regime} className="persistence-item">
              
              {/* Tên Regime + Dot màu */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div 
                  className="regime-dot" 
                  style={{ 
                    backgroundColor: getRegimeColor(regime), 
                    width: '8px', 
                    height: '8px',
                    borderRadius: '2px' 
                  }} 
                />
                <span style={{ fontWeight: 700, color: '#f8fafc' }}>{regime}</span>
              </div>

              {/* Thông số thống kê */}
              <div style={{ color: '#94a3b8' }}>
                {stats.avg.toFixed(1)}d mean lifespan ({stats.count} transitions)
              </div>
            </div>
          ))}
      </div>
    </div>
  );
};