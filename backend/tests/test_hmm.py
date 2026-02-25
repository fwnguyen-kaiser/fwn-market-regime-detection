import numpy as np
import pytest
from app.engine.hmm_model import RegimeDetector 

def test_regime_detector_integrity():
    n_states = 3
    detector = RegimeDetector(n_states=n_states, random_state=42)
    
    # Tạo dữ liệu có 3 cụm rõ rệt
    bear_market = np.random.randn(100, 1) * 0.01 - 0.03   # Giảm
    sideways_market = np.random.randn(100, 1) * 0.01      # Đi ngang
    bull_market = np.random.randn(100, 1) * 0.01 + 0.03   # Tăng
    
    mock_returns = np.vstack([bear_market, sideways_market, bull_market])
    
    import pandas as pd
    df_mock = pd.DataFrame({
        'Log_Return': mock_returns.flatten(),
        'Volatility': np.random.rand(300) * 0.01 
    })

    # Fit và Predict
    detector.fit(mock_returns, verbose=False)
    states = detector.predict_states(mock_returns)

    # Gán ý nghĩa và Kiểm tra độ ổn định
    detector.assign_regime_meaning(df_mock, states) 
    persistence = detector.validate_persistence(states)
    
    # Assertion (Chốt hạ kết quả)
    assert len(detector.regime_mapping) == n_states
    assert "Bull" in detector.regime_mapping.values()
    assert "Bear" in detector.regime_mapping.values()
    assert persistence['persistence_score'] > 0

def test_hmm_parameter_counting():
    """
    Kiểm tra hàm đếm parameter (logic nội bộ của bro)
    """
    detector = RegimeDetector(n_states=2)
    detector.model.n_features = 1
    n_params = detector._count_parameters()
    
    assert n_params == 7