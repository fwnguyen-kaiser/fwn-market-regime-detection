# app/services/pipeline_service.py
import logging
import pandas as pd
import numpy as np
from app.services.data_service import DataService
from app.engine.features import HMMPreprocessor
from app.engine.hmm_model import RegimeDetector, HMMPredictor
from app.engine.model_config import model_config

logger = logging.getLogger(__name__)

class PipelineService:
    """
    Orchestrates the complete market regime detection workflow.
    Handles: data ingestion → feature engineering → HMM training → prediction
    """
    
    def __init__(self):
        self.data_service = DataService()
    
    def run_analysis_on_file(self, filename: str, n_states: int = None) -> dict:
        """
        Execute full HMM analysis pipeline on dataset.
        
        Args:
            filename: CSV file in data directory
            n_states: Number of hidden states (default: use config)
        
        Returns:
            dict: Complete analysis with training stats, regimes, prediction
        """
        logger.info("="*60)
        logger.info(f"🚀 PIPELINE START: {filename}")
        logger.info("="*60)
        
        # === Step 1: Load Data ===
        try:
            df_raw = self.data_service.load_dataset(filename)
        except FileNotFoundError as e:
            logger.error(f"❌ Dataset not found: {e}")
            raise
        
        # Limit data to recent window for better model sensitivity
        max_days = model_config.MAX_TRAINING_DAYS
        original_length = len(df_raw)
        
        if original_length > max_days:
            logger.info(f"⚠️ Truncating data: {original_length} → {max_days} days")
            df_raw = df_raw.tail(max_days)
        
        # === Step 2-3: Feature Engineering ===
        prep_result = HMMPreprocessor.csv_to_features(df_raw)
        df = prep_result['df']
        scaled_features = prep_result['scaled_features']
        
        # === Step 4: Model Configuration ===
        if n_states is None:
            n_states = model_config.DEFAULT_N_STATES
            logger.info(f"📌 Using config: n_states={n_states}")
        else:
            logger.info(f"📌 Manual override: n_states={n_states}")
        
        # === Step 5: Train HMM ===
        detector = RegimeDetector(n_states=n_states)
        detector.fit(scaled_features)
        
        # === Step 6: Decode States ===
        states = detector.predict_states(scaled_features)
        
        # === Step 7: Assign Meanings ===
        state_stats = detector.assign_regime_meaning(df, states)
        
        # === Step 8: Validate Persistence ===
        persistence = detector.validate_persistence(states)
        
        # === Step 9: Predict t+1 ===
        predictor = HMMPredictor(detector, state_stats)
        prediction = predictor.get_prediction_details(scaled_features)
        
        # === Prepare Output ===
        df['State'] = states
        df['Regime'] = df['State'].map(detector.regime_mapping)
        
        current_state = int(states[-1])
        current_regime = detector.regime_mapping.get(current_state, "Unknown")
        
        # Get last 30 days of regime history
        lookback = 30
        recent_states = states[-lookback:] if len(states) >= lookback else states
        recent_dates = df.index[-len(recent_states):]
        
        regime_history = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'regime': detector.regime_mapping.get(s, "Unknown")
            }
            for date, s in zip(recent_dates, recent_states)
        ]
        
        model_params = detector.get_model_params()
        
        logger.info("="*60)
        logger.info("✅ PIPELINE COMPLETE")
        logger.info("="*60)
        
        return {
            "filename": filename,
            "total_days": len(df),
            "n_states": n_states,
            "features_used": prep_result['feature_cols'],
            "model_selection": None,  # Not using auto-selection
            "training_stats": detector.training_stats,
            "regime_mapping": detector.regime_mapping,
            "state_statistics": state_stats,
            "persistence": persistence,
            "current_regime": current_regime,
            "current_state": current_state,
            "prediction": prediction,
            "regime_history": regime_history,
            "model_params": {
                "start_probs": model_params['start_probs'].tolist(),
                "transition_matrix": model_params['transition_matrix'].tolist(),
            }
        }