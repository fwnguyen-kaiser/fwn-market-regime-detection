# app/engine/hmm_model.py
from hmmlearn import hmm
import numpy as np
import pandas as pd
from app.engine.model_config import model_config
import logging

logger = logging.getLogger(__name__)

class RegimeDetector:
    """
    HMM Model for Regime Detection
    Steps 4-8: Chọn n_states → Fit → Decode → Meaning → Validate
    """
    
    def __init__(self, n_states: int = None, random_state: int = None): # pyright: ignore[reportArgumentType]
        """
        Step 4: Initialize HMM with config
        """
        self.n_states = n_states or model_config.DEFAULT_N_STATES
        self.random_state = random_state or model_config.RANDOM_STATE
        
        logger.info(f"🤖 Initializing HMM with {self.n_states} states")
        
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type=model_config.COVARIANCE_TYPE,
            n_iter=model_config.MAX_EM_ITERATIONS,
            random_state=self.random_state,
            tol=model_config.CONVERGENCE_TOLERANCE,
            verbose=False
        )
        
        self.is_trained = False
        self.training_stats = {}
        self.regime_mapping = {}
    
    def fit(self, features: np.ndarray, verbose: bool = True):
        """
        Step 5: Fit HMM using EM algorithm
        """
        if verbose:
            logger.info(f"🤖 Training HMM: {features.shape[0]} samples, {features.shape[1]} features, {self.n_states} states")
        
        # Train model
        self.model.fit(features)
        
        # Calculate metrics
        log_likelihood = self.model.score(features)
        n_params = self._count_parameters()
        n_samples = features.shape[0]
        
        aic = -2 * log_likelihood + 2 * n_params
        bic = -2 * log_likelihood + n_params * np.log(n_samples)
        
        self.training_stats = {
            'log_likelihood': log_likelihood,
            'aic': aic,
            'bic': bic,
            'n_params': n_params,
            'n_iter': self.model.monitor_.iter,
            'converged': self.model.monitor_.converged
        }
        
        if verbose:
            logger.info(f"   ✅ Converged: {self.training_stats['converged']}, "
                       f"Iterations: {self.training_stats['n_iter']}, "
                       f"BIC: {bic:.2f}")
        
        self.is_trained = True
        return self
    
    def _count_parameters(self) -> int:
        """Count total HMM parameters"""
        n = self.n_states
        d = self.model.n_features
        
        # Transition matrix + Start probs + Means + Covariances
        n_params = n * (n - 1) + (n - 1) + n * d + n * d * (d + 1) // 2
        return n_params
    
    def predict_states(self, features: np.ndarray) -> np.ndarray:
        """
        Step 6: Decode states using Viterbi algorithm
        """
        if not self.is_trained:
            raise ValueError("Model chưa được train! Call fit() trước.")
        
        logger.info("🔮 Decoding states with Viterbi...")
        states = self.model.predict(features)
        
        logger.info(f"   ✅ Decoded {len(states)} states, unique: {np.unique(states)}")
        return states
    
    def assign_regime_meaning(self, df: pd.DataFrame, states: np.ndarray) -> dict:
        """
        Step 7: Assign semantic meaning (Bear/Bull/Sideways) to states
        based on average returns
        """
        logger.info("🏷️  Assigning regime meanings...")
        
        df_copy = df.copy()
        df_copy['State'] = states
        
        # Calculate stats for each state
        state_stats = {}
        for state in range(self.n_states):
            state_data = df_copy[df_copy['State'] == state]
            
            if len(state_data) > 0:
                state_stats[state] = {
                    'count': len(state_data),
                    'mean_return': state_data['Log_Return'].mean(),
                    'std_return': state_data['Log_Return'].std(),
                    'mean_volatility': state_data['Volatility'].mean(),
                    'std_volatility': state_data['Volatility'].std(),
                }
            else:
                state_stats[state] = {
                    'count': 0,
                    'mean_return': 0,
                    'std_return': 0,
                    'mean_volatility': 0,
                    'std_volatility': 0,
                }
        
        # Sort states by mean return (low to high)
        sorted_states = sorted(state_stats.items(), 
                              key=lambda x: x[1]['mean_return'])
        
        # Assign labels based on n_states
        self.regime_mapping = {}
        
        if self.n_states == 2:
            self.regime_mapping = {
                sorted_states[0][0]: "Bear",
                sorted_states[1][0]: "Bull"
            }
        elif self.n_states == 3:
            self.regime_mapping = {
                sorted_states[0][0]: "Bear",
                sorted_states[1][0]: "Sideways",
                sorted_states[2][0]: "Bull"
            }
        elif self.n_states == 4:
            # For 4 states, consider volatility too
            mid_states = sorted(sorted_states[1:3], 
                              key=lambda x: x[1]['mean_volatility'])
            self.regime_mapping = {
                sorted_states[0][0]: "Bear",
                mid_states[0][0]: "Low_Volatility",
                mid_states[1][0]: "High_Volatility", 
                sorted_states[3][0]: "Bull"
            }
        else:
            # Generic naming for n>4
            for i, (state, _) in enumerate(sorted_states):
                self.regime_mapping[state] = f"Regime_{i}"
        
        logger.info(f"   ✅ Mapped: {self.regime_mapping}")
        return state_stats
    
    def validate_persistence(self, states: np.ndarray) -> dict:
        """
        Step 8: Validate regime persistence
        Measures how stable regimes are (do they last long enough?)
        """
        logger.info("✅ Validating persistence...")
        
        # Count regime switches
        n_switches = np.sum(np.diff(states) != 0)
        
        # Calculate regime durations
        regime_lengths = []
        current_length = 1
        
        for i in range(1, len(states)):
            if states[i] == states[i-1]:
                current_length += 1
            else:
                regime_lengths.append(current_length)
                current_length = 1
        regime_lengths.append(current_length)
        
        avg_duration = np.mean(regime_lengths)
        min_duration = np.min(regime_lengths)
        max_duration = np.max(regime_lengths)
        median_duration = np.median(regime_lengths)
        persistence_score = avg_duration / len(states)
        
        # Calculate duration by regime
        duration_by_regime = {}
        current_state = states[0]
        current_dur = 1
        durations_dict = {i: [] for i in range(self.n_states)}
        
        for i in range(1, len(states)):
            if states[i] == current_state:
                current_dur += 1
            else:
                durations_dict[current_state].append(current_dur)
                current_state = states[i]
                current_dur = 1
        durations_dict[current_state].append(current_dur)
        
        for state in range(self.n_states):
            if len(durations_dict[state]) > 0:
                duration_by_regime[self.regime_mapping[state]] = {
                    'avg': np.mean(durations_dict[state]),
                    'count': len(durations_dict[state])
                }
        
        # Quality assessment using config thresholds
        if persistence_score > model_config.GOOD_PERSISTENCE_THRESHOLD:
            quality = "🟢 GOOD - Stable regimes"
        elif persistence_score > model_config.MODERATE_PERSISTENCE_THRESHOLD:
            quality = "🟡 MODERATE - Some noise"
        else:
            quality = "🔴 POOR - Too much switching (overfitting?)"
        
        logger.info(f"   Persistence: {persistence_score:.1%}, Quality: {quality}")
        
        return {
            'total_switches': int(n_switches),
            'avg_duration': float(avg_duration),
            'median_duration': float(median_duration),
            'min_duration': int(min_duration),
            'max_duration': int(max_duration),
            'persistence_score': float(persistence_score),
            'duration_by_regime': duration_by_regime,
            'quality': quality
        }
    
    def get_model_params(self) -> dict:
        """Get trained model parameters"""
        if not self.is_trained:
            raise ValueError("Model chưa được train!")
        
        return {
            'start_probs': self.model.startprob_,
            'transition_matrix': self.model.transmat_,
            'means': self.model.means_,
            'covariances': self.model.covars_
        }


class HMMPredictor:
    """
    Predict future regime (t+1) based on trained HMM
    Uses transition matrix and current state probabilities
    """
    
    def __init__(self, detector: RegimeDetector, state_stats: dict):
        if not detector.is_trained:
            raise ValueError("RegimeDetector must be trained first!")
        
        self.detector = detector
        self.model = detector.model
        self.state_stats = state_stats
        self.regime_mapping = detector.regime_mapping
    
    def predict_next_proba(self, features: np.ndarray) -> np.ndarray:
        """
        Predict probability distribution for next state
        Formula: P(s_t+1) = P(s_t) @ A (transition matrix)
        """
        # Get current state probabilities
        state_probs = self.model.predict_proba(features)
        last_prob = state_probs[-1]
        
        # Apply transition matrix
        A = self.model.transmat_
        next_prob = last_prob @ A
        
        return next_prob
    
    def get_prediction_details(self, features: np.ndarray) -> dict:
        """
        Get comprehensive prediction for t+1
        Includes: most likely regime, confidence, expected return/volatility
        """
        logger.info("🔮 Predicting t+1...")
        
        next_prob = self.predict_next_proba(features)
        next_state = int(np.argmax(next_prob))
        next_regime = self.regime_mapping[next_state]
        
        # Build regime probabilities dict
        regime_probs = {
            self.regime_mapping[i]: float(prob)
            for i, prob in enumerate(next_prob)
        }
        
        # Calculate expected return and volatility
        expected_return = sum(
            next_prob[i] * self.state_stats[i]['mean_return']
            for i in range(len(next_prob))
        )
        
        expected_vol = sum(
            next_prob[i] * self.state_stats[i]['mean_volatility']
            for i in range(len(next_prob))
        )
        
        confidence = float(np.max(next_prob))
        
        logger.info(f"   Most likely: {next_regime} ({confidence*100:.1f}% confidence)")
        
        return {
            'next_state': next_state,
            'next_regime': next_regime,
            'state_probabilities': regime_probs,
            'expected_return': float(expected_return),
            'expected_volatility': float(expected_vol),
            'confidence': confidence
        }


class ModelSelector:
    """
    Auto-select optimal n_states using BIC
    """
    
    @staticmethod
    def select_best_n_states(features: np.ndarray, 
                            min_states: int = None,  # pyright: ignore[reportArgumentType]
                            max_states: int = None, # pyright: ignore[reportArgumentType]
                            random_state: int = None) -> dict: # pyright: ignore[reportArgumentType]
        """
        Test multiple n_states and choose best based on BIC
        """
        min_states = min_states or model_config.MIN_N_STATES
        max_states = max_states or model_config.MAX_N_STATES
        random_state = random_state or model_config.RANDOM_STATE
        
        logger.info("🔍 Auto-selecting optimal n_states...")
        
        results = []
        
        for n in range(min_states, max_states + 1):
            detector = RegimeDetector(n_states=n, random_state=random_state)
            detector.fit(features, verbose=False)
            
            results.append({
                'n_states': n,
                'bic': detector.training_stats['bic'],
                'aic': detector.training_stats['aic'],
                'log_likelihood': detector.training_stats['log_likelihood']
            })
            
            logger.info(f"   n={n}: BIC={detector.training_stats['bic']:.2f}")
        
        best_idx = np.argmin([r['bic'] for r in results])
        optimal_n = results[best_idx]['n_states']
        
        logger.info(f"✅ Optimal n_states: {optimal_n}")
        
        return {
            'optimal_n_states': optimal_n,
            'all_results': results
        }