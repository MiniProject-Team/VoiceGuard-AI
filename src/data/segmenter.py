"""Fixed-window overlapping audio segmentation."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Segment:
    audio: np.ndarray
    index: int
    start_time: float
    end_time: float
    duration: float
    padding_applied: bool


def segment_audio(audio: np.ndarray, sample_rate: int, duration_seconds: float = 5.0,
                  hop_seconds: float = 2.5, short_audio_policy: str = "pad") -> list[Segment]:
    """Return full windows; pad a short/tail window only when no full window exists."""
    if duration_seconds <= 0 or hop_seconds <= 0:
        raise ValueError("Segment and hop durations must be positive")
    data = np.asarray(audio, dtype=np.float32).reshape(-1)
    window, hop = round(duration_seconds * sample_rate), round(hop_seconds * sample_rate)
    if window <= 0 or hop <= 0:
        raise ValueError("Durations are too small for the sample rate")
    if len(data) < window:
        if short_audio_policy == "skip":
            return []
        if short_audio_policy != "pad":
            raise ValueError("short_audio_policy must be 'pad' or 'skip'")
        padded = np.pad(data, (0, window - len(data)))
        return [Segment(padded, 0, 0.0, len(data) / sample_rate, len(data) / sample_rate, True)]
    starts = range(0, len(data) - window + 1, hop)
    return [Segment(data[start:start + window].copy(), index, start / sample_rate,
                    (start + window) / sample_rate, duration_seconds, False)
            for index, start in enumerate(starts)]
