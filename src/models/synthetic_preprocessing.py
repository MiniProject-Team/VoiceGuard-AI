"""Shared, non-persistent waveform preparation for Phase 3 inference."""
from __future__ import annotations

import numpy as np

from src.data.audio_utils import convert_to_mono, normalize_audio, resample_audio


def prepare_synthetic_waveform(
    waveform: np.ndarray,
    source_sample_rate: int,
    target_sample_rate: int,
    max_duration_seconds: float,
    *,
    pad_to_duration: bool = True,
) -> np.ndarray:
    """Apply the Phase 2/3 mono, resampling, normalization, and window policy.

    The returned array is memory-only float32 data.  Padding makes a standalone
    inference window match the fixed five-second segments used to train Phase 3.
    """
    if source_sample_rate <= 0 or target_sample_rate <= 0:
        raise ValueError("Sample rates must be positive.")
    data = convert_to_mono(np.asarray(waveform, dtype=np.float32))
    if not data.size:
        raise ValueError("Audio is empty.")
    if not np.isfinite(data).all():
        raise ValueError("Audio contains NaN or infinite values.")
    data = resample_audio(data, source_sample_rate, target_sample_rate)
    data = normalize_audio(data)
    target_samples = round(target_sample_rate * max_duration_seconds)
    data = data[:target_samples]
    if pad_to_duration and data.size < target_samples:
        data = np.pad(data, (0, target_samples - data.size))
    return np.asarray(data, dtype=np.float32)


def waveform_statistics(waveform: np.ndarray, sample_rate: int) -> dict[str, float | int | list[int]]:
    """Return safe aggregate diagnostics; never include waveform samples."""
    data = np.asarray(waveform, dtype=np.float32)
    return {
        "sample_rate": int(sample_rate),
        "duration_seconds": round(float(data.size / sample_rate), 6),
        "shape": list(data.shape),
        "minimum": float(data.min()),
        "maximum": float(data.max()),
        "mean": float(data.mean()),
        "std": float(data.std()),
    }
