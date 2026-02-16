# app/engine/features.py
import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler
from app.engine.model_config import model_config

logger = logging.getLogger(__name__)

class FeatureEngine:
    """
    Transform raw OHLC data into features for HMM:
    - Log returns (stationary)
    - Volatility (rolling std)
    """
    
    @staticmethod
    def load_ohlc(df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 1: Load and clean OHLC data
        - Set Date as index
        - Sort chronologically
        - Validate required columns
        """
        if 'Date' in df.columns:
            df = df.set_index('Date')
        
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Check required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
        
        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        logger.info(f"📊 Loaded {len(df)} trading days ({df.index[0].date()} to {df.index[-1].date()})")
        
        return df[required_cols]
    
    @staticmethod
    def calculate_log_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 2a: Calculate log returns
        Formula: r_t = ln(P_t / P_t-1)
        Log returns are time-additive and more stationary
        """
        logger.info("   → Calculating log returns...")
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        return df
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame, window: int = None) -> pd.DataFrame:
        """
        Step 2b: Calculate realized volatility
        Uses rolling standard deviation of log returns
        """
        window = window or model_config.VOLATILITY_WINDOW
        
        logger.info(f"   → Calculating volatility (window={window})...")
        
        # Rolling std of log returns
        df['Volatility'] = df['Log_Return'].rolling(window=window).std()
        
        # Annualized for reference
        df['Volatility_Annualized'] = df['Volatility'] * np.sqrt(252)
        
        return df
    
    @staticmethod
    def prepare_features(df: pd.DataFrame, vol_window: int = None) -> pd.DataFrame:
        """
        Step 2: Create all features and clean NaNs
        """
        vol_window = vol_window or model_config.VOLATILITY_WINDOW
        
        logger.info("📊 Engineering features...")
        
        df = FeatureEngine.calculate_log_returns(df)
        df = FeatureEngine.calculate_volatility(df, window=vol_window)
        
        # Drop NaN rows (from shift and rolling)
        initial_len = len(df)
        df = df.dropna()
        dropped = initial_len - len(df)
        
        logger.info(f"   ✅ Dropped {dropped} NaN rows, {len(df)} rows ready")
        
        return df
    
    @staticmethod
    def scale_features(df: pd.DataFrame, feature_cols: list = None) -> tuple:
        """
        Step 3: Scale features using StandardScaler
        HMMs require normalized data (mean=0, std=1) for stable EM convergence
        """
        feature_cols = feature_cols or model_config.FEATURES
        
        logger.info(f"📊 Scaling features: {feature_cols}...")
        
        # Validate columns exist
        missing = [col for col in feature_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing features: {missing}")
        
        features_raw = df[feature_cols].values
        
        # Standardize (mean=0, std=1)
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features_raw)
        
        logger.info(f"   ✅ Scaled: mean≈0, std≈1")
        
        return features_scaled, scaler, feature_cols


class HMMPreprocessor:
    """
    Full preprocessing pipeline: CSV → Scaled features for HMM
    """
    
    @staticmethod
    def csv_to_features(df: pd.DataFrame, vol_window: int = None) -> dict:
        """
        Execute full pipeline:
        1. Load & clean OHLC
        2. Engineer features (log returns, volatility)
        3. Scale features
        
        Returns dict with:
        - df: processed DataFrame
        - scaled_features: numpy array for HMM
        - scaler: StandardScaler object
        - feature_cols: list of feature names
        """
        vol_window = vol_window or model_config.VOLATILITY_WINDOW
        
        logger.info("="*60)
        logger.info("🔄 PREPROCESSING PIPELINE: CSV → HMM Features")
        logger.info("="*60)
        
        try:
            # Step 1: Load & clean
            df_clean = FeatureEngine.load_ohlc(df)
            
            # Step 2: Feature engineering
            df_features = FeatureEngine.prepare_features(df_clean, vol_window=vol_window)
            
            # Step 3: Scaling
            scaled_features, scaler, feature_cols = FeatureEngine.scale_features(df_features)
            
            logger.info("="*60)
            logger.info("✅ PREPROCESSING COMPLETE")
            logger.info("="*60)
            
            return {
                'df': df_features,
                'scaled_features': scaled_features,
                'scaler': scaler,
                'feature_cols': feature_cols,
                'n_samples': len(df_features)
            }
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            raise