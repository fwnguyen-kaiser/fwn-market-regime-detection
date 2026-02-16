"""
Model Configuration Engine - Specialized for Market Regime Persistence
Defines hyperparameters for HMM training, feature engineering, and state classification.
"""

class ModelConfig:
    """
    Centralized configuration for the HMM detection engine.
    Optimized for financial time-series stability and regime consistency.
    """
    
    # --- Feature Engineering Parameters ---
    # Lookback window for rolling volatility to filter out high-frequency noise
    VOLATILITY_WINDOW = 30 
    
    # --- HMM Hyperparameters ---
    # Optimal state count for financial markets: typically Bear, Sideways, and Bull
    DEFAULT_N_STATES = 3 
    COVARIANCE_TYPE = "full"  # Allows for more complex relationship between features
    MAX_EM_ITERATIONS = 1000  # Maximum Expectation-Maximization cycles
    CONVERGENCE_TOLERANCE = 1e-4
    RANDOM_STATE = 42
    
    # --- Automated Model Selection (AIC/BIC) ---
    MIN_N_STATES = 2
    MAX_N_STATES = 4  # Restricted to avoid overfitting and redundant state splitting
    SELECTION_METRIC = "bic"  # Bayesian Information Criterion favors parsimonious models
    
    # --- Regime Persistence & Stability ---
    # Minimum consecutive days to qualify as a valid regime transition
    MIN_REGIME_DURATION = 5
    # Probability thresholds for evaluating model 'quality' and state stability
    GOOD_PERSISTENCE_THRESHOLD = 0.10 
    MODERATE_PERSISTENCE_THRESHOLD = 0.05 
    
    # --- Data Windowing ---
    # Limits training to the most recent window to account for market structural shifts
    MAX_TRAINING_DAYS = 500 
    
    # --- Semantic Regime Mapping ---
    # Maps latent HMM states to financial terminology based on mean return/volatility
    REGIME_NAMES_2_STATES = {
        "low": "Bear",
        "high": "Bull"
    }
    
    REGIME_NAMES_3_STATES = {
        "low": "Bear",
        "mid": "Sideways",
        "high": "Bull"
    }
    
    REGIME_NAMES_4_STATES = {
        "lowest": "Bear",
        "low_vol": "Low_Volatility",
        "high_vol": "High_Volatility",
        "highest": "Bull"
    }
    
    # --- Inference & Prediction ---
    # Confidence requirement for t+1 probability-based forecasting
    PREDICTION_CONFIDENCE_THRESHOLD = 0.6
    
    # --- Data Normalization ---
    FEATURES = ["Log_Return", "Volatility"]
    SCALING_METHOD = "standard"  # Z-score normalization for stationary features
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """
        Exports a snapshot of active hyperparameters for logging and audit trails.
        """
        return {
            "volatility_window": cls.VOLATILITY_WINDOW,
            "default_n_states": cls.DEFAULT_N_STATES,
            "max_training_days": cls.MAX_TRAINING_DAYS,
            "good_threshold": cls.GOOD_PERSISTENCE_THRESHOLD,
            "moderate_threshold": cls.MODERATE_PERSISTENCE_THRESHOLD,
            "features": cls.FEATURES,
        }

# Singleton instance for global access across the engine
model_config = ModelConfig()