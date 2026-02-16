from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional

class MessageResponse(BaseModel):
    """Standard response for operational success messages."""
    message: str
    filename: str

class RegimeHistoryItem(BaseModel):
    """Represents a single historical data point for regime tracking."""
    date: str
    regime: str

class PersistenceMetrics(BaseModel):
    """Statistical metrics evaluating the stability and duration of detected regimes."""
    total_switches: int
    avg_duration: float
    median_duration: float
    min_duration: int
    max_duration: int
    persistence_score: float
    duration_by_regime: Dict[str, Dict[str, float]]
    quality: str

class PredictionResponse(BaseModel):
    """Probabilistic forecasting for the next immediate time step (t+1)."""
    next_state: int
    next_regime: str
    state_probabilities: Dict[str, float]
    expected_return: float
    expected_volatility: float
    confidence: float

class AnalysisResponse(BaseModel):
    """
    Comprehensive schema for the full HMM analysis output.
    
    Attributes:
        model_config: Configured to suppress protected namespace warnings 
                      arising from fields starting with 'model_'.
    """
    model_config = ConfigDict(protected_namespaces=())
    
    filename: str
    total_days: int
    n_states: int
    features_used: List[str]
    model_selection: Optional[List[Dict[str, Any]]] = None
    training_stats: Dict[str, Any]
    regime_mapping: Dict[int, str]
    state_statistics: Dict[int, Dict[str, float]]
    persistence: PersistenceMetrics
    current_regime: str
    current_state: int
    prediction: PredictionResponse
    regime_history: List[RegimeHistoryItem]
    model_params: Dict[str, Any]