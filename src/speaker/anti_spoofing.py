"""Extension point for future replay detection; no Phase 4 replay model is implemented."""
from __future__ import annotations
from typing import Protocol
import numpy as np

class ReplayDetector(Protocol):
    """Future implementations may produce an independent replay-attack score."""
    def score(self, waveform: np.ndarray, sample_rate: int) -> float: ...
