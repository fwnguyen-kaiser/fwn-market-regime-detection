// src/components/PredictionCard.tsx
import React from 'react';
import type { PredictionResult } from '../types/regime';

interface Props {
  prediction: PredictionResult;
}

export const PredictionCard: React.FC<Props> = ({ prediction }) => {
  const getRegimeColor = (regime: string) => {
    if (regime.includes('Bull')) return '#10b981';
    if (regime.includes('Bear')) return '#ef4444';
    if (regime.includes('Sideways') || regime.includes('High')) return '#f59e0b';
    return '#8b5cf6';
  };

  const getConfidenceColor = (conf: number) => {
    if (conf > 0.7) return '#34d399';
    if (conf > 0.5) return '#fbbf24';
    return '#f87171';
  };

  return (
    <div className="prediction-card-container">
      <div className="prediction-main-banner">
        <div className="prediction-icon-bg">🔮</div>
        
        <div className="prediction-info">
          <div className="prediction-label">Next Phase Prediction (t+1)</div>
          <div 
            className="prediction-value" 
            style={{ color: getRegimeColor(prediction.next_regime) }}
          >
            {prediction.next_regime}
          </div>
          <div className="prediction-confidence-wrapper">
            <span>Confidence:</span>
            <span style={{ 
              color: getConfidenceColor(prediction.confidence), 
              fontWeight: 700,
              fontSize: '1.1rem'
            }}>
              {(prediction.confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        <div className="metrics-grid">
          <div className="metric-box">
            <div className="metric-label">Expected Return</div>
            <div 
              className="metric-value" 
              style={{ color: prediction.expected_return >= 0 ? '#10b981' : '#ef4444' }}
            >
              {prediction.expected_return >= 0 ? '+' : ''}
              {(prediction.expected_return * 100).toFixed(2)}%
            </div>
          </div>

          <div className="metric-box">
            <div className="metric-label">Expected Vol</div>
            <div className="metric-value" style={{ color: '#e2e8f0' }}>
              {(prediction.expected_volatility * 100).toFixed(2)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};