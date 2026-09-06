"""Safe signal normalization and weighted contributions."""
from __future__ import annotations
import math

def clamp(value: float, minimum: float, maximum: float) -> float: return max(minimum, min(maximum, value))
def normalize_probability(value: float | None) -> float | None:
    if value is None: return None
    if not math.isfinite(float(value)): raise ValueError("Probability must be finite")
    return clamp(float(value), 0., 1.)
def normalize_similarity(value: float | None, minimum: float = -1., maximum: float = 1.) -> float | None:
    if value is None: return None
    if maximum <= minimum: raise ValueError("Similarity calibration maximum must exceed minimum")
    if not math.isfinite(float(value)): raise ValueError("Similarity must be finite")
    return clamp((float(value) - minimum) / (maximum - minimum), 0., 1.)
def speaker_mismatch(similarity: float | None, calibrated_probability: float | None, minimum=-1., maximum=1.) -> float | None:
    if calibrated_probability is not None: return normalize_probability(calibrated_probability)
    normalized = normalize_similarity(similarity, minimum, maximum)
    return None if normalized is None else 1. - normalized
def weighted_contribution(normalized: float | None, weight: float, enabled: bool = True) -> float:
    return 0. if normalized is None or not enabled else normalized * float(weight) * 100.
