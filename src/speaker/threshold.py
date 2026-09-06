"""Validation-only speaker operating-threshold analysis."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

def metrics_at_threshold(labels: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float]:
    y, accepted = np.asarray(labels, dtype=int), np.asarray(scores) >= threshold
    genuine, impostor = y == 1, y == 0
    ta, fr = int(np.sum(accepted & genuine)), int(np.sum(~accepted & genuine))
    fa, tr = int(np.sum(accepted & impostor)), int(np.sum(~accepted & impostor))
    safe = lambda a, b: float(a / b) if b else 0.0
    return {"threshold": float(threshold), "TAR": safe(ta, ta + fr), "FAR": safe(fa, fa + tr),
            "FRR": safe(fr, ta + fr), "accuracy": safe(ta + tr, len(y))}

def analyze_thresholds(labels: np.ndarray, scores: np.ndarray, start=.2, stop=.95, step=.05) -> pd.DataFrame:
    return pd.DataFrame([metrics_at_threshold(labels, scores, value) for value in np.arange(start, stop + step / 2, step)])

def calculate_eer(labels: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    if len(np.unique(labels)) != 2: raise ValueError("EER requires genuine and impostor trials")
    far, tar, thresholds = roc_curve(labels, scores, pos_label=1); frr = 1 - tar; index = int(np.nanargmin(np.abs(far - frr)))
    return float((far[index] + frr[index]) / 2), float(thresholds[index])

def select_threshold(validation_trials: pd.DataFrame, criterion: str = "eer") -> tuple[float, pd.DataFrame]:
    labels = (validation_trials["trial_type"] == "genuine").astype(int).to_numpy(); scores = validation_trials["similarity"].to_numpy()
    analysis = analyze_thresholds(labels, scores)
    if criterion == "eer": _, threshold = calculate_eer(labels, scores)
    elif criterion == "accuracy": threshold = float(analysis.loc[analysis.accuracy.idxmax(), "threshold"])
    else: raise ValueError("criterion must be 'eer' or 'accuracy'")
    return threshold, analysis
