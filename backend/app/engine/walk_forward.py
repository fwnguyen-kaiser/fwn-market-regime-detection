# app/engine/walk_forward.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Optional, Tuple
from app.engine.hmm_model import RegimeDetector
import logging

logger = logging.getLogger(__name__)


def _resolve_label_flip(
    regime_mapping: dict,
    reference_signatures: Optional[dict],
    state_stats: dict,
) -> Tuple[dict, dict]:
    """
    Prevent label flips across folds by matching each state to the
    closest reference centroid (mean_return, mean_volatility).
    On the first fold, the mapping is taken as the reference.
    """
    if reference_signatures is None:
        # First fold — use as-is, capture signatures
        return regime_mapping, {
            label: (state_stats[state]["mean_return"], state_stats[state]["mean_volatility"])
            for state, label in regime_mapping.items()
        }

    # Build candidate signatures for this fold
    candidate = {
        state: (state_stats[state]["mean_return"], state_stats[state]["mean_volatility"])
        for state in regime_mapping
    }

    # Greedy nearest-centroid match
    new_mapping = {}
    used_labels = set()
    for state, (r, v) in candidate.items():
        best_label, best_dist = None, float("inf")
        for label, (ref_r, ref_v) in reference_signatures.items():
            if label in used_labels:
                continue
            dist = (r - ref_r) ** 2 + (v - ref_v) ** 2
            if dist < best_dist:
                best_dist, best_label = dist, label
        new_mapping[state] = best_label
        used_labels.add(best_label)

    return new_mapping, reference_signatures  # keep original as reference


def walk_forward_validation(
    df: pd.DataFrame,
    feature_cols: list[str],
    n_states: int = 3,
    train_size: int = 500,    # initial training window (bars)
    test_size: int = 60,      # bars per fold
    step_size: int = 60,      # how far to advance each fold
    expanding: bool = True,   # True = expanding window, False = rolling
) -> dict:                    # ✅ FIXED: returns ONE dict, not a tuple
    """
    Walk-forward validation for HMM regime detection.

    No fake accuracy metric — HMM is UNSUPERVISED, there is no ground truth.
    Instead, we track:
      - BIC per fold (model quality)
      - Regime distribution per fold (stability check)
      - Convergence per fold
    """
    logger.info("=" * 60)
    logger.info("Walk-Forward Validation")
    logger.info(f"  n_states={n_states}, train_size={train_size}, "
                f"test_size={test_size}, step_size={step_size}, expanding={expanding}")
    logger.info("=" * 60)

    features_all = df[feature_cols].values
    n_total = len(df)

    fold_results = []
    reference_signatures = None

    fold = 0
    train_end = train_size

    while train_end + test_size <= n_total:
        train_start = 0 if expanding else (train_end - train_size)
        test_start  = train_end
        test_end    = train_end + test_size

        X_train = features_all[train_start:train_end]
        X_test  = features_all[test_start:test_end]
        df_train = df.iloc[train_start:train_end].copy()

        # ── Scaler fit on TRAIN only (no leakage) ────────────────────────
        scaler = StandardScaler()
        X_train_sc = scaler.fit_transform(X_train)
        X_test_sc  = scaler.transform(X_test)

        # ── Train HMM on TRAIN window ─────────────────────────────────────
        detector = RegimeDetector(n_states=n_states)
        detector.fit(X_train_sc, verbose=False)

        # ── Decode TRAIN states (for label assignment, no leakage) ────────
        train_states = detector.predict_states(X_train_sc)
        df_train["State"] = train_states

        # Assign meanings from TRAIN stats only
        state_stats = {}
        for state in range(n_states):
            mask = df_train["State"] == state
            sub  = df_train[mask]
            state_stats[state] = {
                "count":           int(mask.sum()),
                "mean_return":     float(sub["Log_Return"].mean()) if len(sub) else 0.0,
                "std_return":      float(sub["Log_Return"].std())  if len(sub) else 0.0,
                "mean_volatility": float(sub["Volatility"].mean()) if len(sub) else 0.0,
                "std_volatility":  float(sub["Volatility"].std())  if len(sub) else 0.0,
            }
        detector.state_stats = state_stats

        # Build initial regime mapping from sorted returns
        sorted_states = sorted(state_stats.items(), key=lambda x: x[1]["mean_return"])
        labels = {2: ["Bear", "Bull"], 3: ["Bear", "Sideways", "Bull"]}.get(
            n_states, [f"Regime_{i}" for i in range(n_states)]
        )
        raw_mapping = {s[0]: labels[i] for i, s in enumerate(sorted_states)}

        # Resolve label flip vs previous folds
        stable_mapping, reference_signatures = _resolve_label_flip(
            raw_mapping, reference_signatures, state_stats
        )
        detector.regime_mapping = stable_mapping

        # ── Decode TEST states ────────────────────────────────────────────
        test_states = detector.predict_states(X_test_sc)
        df_test = df.iloc[test_start:test_end].copy()
        df_test["State"]  = test_states
        df_test["Regime"] = [stable_mapping[s] for s in test_states]

        # ── Honest metrics (no fake ground truth) ────────────────────────
        # HMM is UNSUPERVISED — we cannot compare against "true" labels.
        # Instead, track regime distribution and BIC stability across folds.
        regime_counts = df_test["Regime"].value_counts().to_dict()

        # Regime switches in test window (lower = more stable)
        n_switches = int(np.sum(np.diff(test_states) != 0))

        fold_info = {
            "fold":          fold + 1,
            "train_range":   [train_start, train_end],
            "test_range":    [test_start, test_end],
            "regime_counts": regime_counts,   # e.g. {"Bull": 30, "Bear": 20, "Sideways": 10}
            "n_switches":    n_switches,       # regime switches in test window
            "bic":           round(detector.training_stats["bic"], 2),
            "converged":     detector.training_stats["converged"],
            "n_iter":        detector.training_stats["n_iter"],
        }
        fold_results.append(fold_info)

        logger.info(
            f"  Fold {fold+1:02d} | train [{train_start}:{train_end}] "
            f"test [{test_start}:{test_end}] | "
            f"regimes={regime_counts} | switches={n_switches} | "
            f"BIC={detector.training_stats['bic']:.1f} | "
            f"converged={detector.training_stats['converged']}"
        )

        fold += 1
        train_end += step_size

    # ── Aggregate summary ─────────────────────────────────────────────────
    bics = [r["bic"] for r in fold_results]
    switches = [r["n_switches"] for r in fold_results]
    converged_count = sum(1 for r in fold_results if r["converged"])

    summary = {
        "n_folds":         len(fold_results),
        "mean_bic":        round(float(np.mean(bics)), 2),
        "std_bic":         round(float(np.std(bics)), 2),
        "min_bic":         round(float(np.min(bics)), 2),
        "max_bic":         round(float(np.max(bics)), 2),
        "mean_switches":   round(float(np.mean(switches)), 2),  # avg regime switches per fold
        "converged_folds": converged_count,                      # how many folds converged
        "fold_results":    fold_results,
    }

    logger.info("=" * 60)
    logger.info(
        f"Summary: mean_BIC={summary['mean_bic']:.2f} ± {summary['std_bic']:.2f} "
        f"over {summary['n_folds']} folds | "
        f"converged={converged_count}/{summary['n_folds']}"
    )
    logger.info("=" * 60)

    return summary  # ✅ ONE dict returned, matches -> dict annotation