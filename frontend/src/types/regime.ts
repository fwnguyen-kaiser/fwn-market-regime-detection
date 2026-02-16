// frontend/src/types/regime.ts
export interface RegimeHistoryItem {
  date: string;
  regime: string;
}

export interface PersistenceMetrics {
  total_switches: number;
  avg_duration: number;
  median_duration: number;
  min_duration: number;
  max_duration: number;
  persistence_score: number;
  duration_by_regime: Record<string, { avg: number; count: number }>;
  quality: string;
}

export interface StateStatistics {
  count: number;
  mean_return: number;
  std_return: number;
  mean_volatility: number;
  std_volatility: number;
}

export interface TrainingStats {
  log_likelihood: number;
  aic: number;
  bic: number;
  n_params: number;
  n_iter: number;
  converged: boolean;
}

export interface AnalysisResult {
  filename: string;
  total_days: number;
  n_states: number;
  features_used: string[];
  model_selection: Array<{
    n_states: number;
    bic: number;
    aic: number;
    log_likelihood: number;
  }> | null;
  training_stats: TrainingStats;
  regime_mapping: Record<number, string>;
  state_statistics: Record<number, StateStatistics>;
  persistence: PersistenceMetrics;
  current_regime: string;
  current_state: number;
  regime_history: RegimeHistoryItem[];
  model_params: {
    start_probs: number[];
    transition_matrix: number[][];
  };
  prediction: PredictionResult;
}
export interface PredictionResult {
  next_state: number;
  next_regime: string;
  state_probabilities: Record<string, number>;
  expected_return: number;
  expected_volatility: number;
  confidence: number;
}