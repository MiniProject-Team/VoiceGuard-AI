"""Reusable audio I/O and conservative standardization."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from math import gcd


def load_audio(path: str | Path) -> tuple[np.ndarray, int]:
    """Load audio as float32; shape is samples or samples x channels."""
    audio, sample_rate = sf.read(Path(path), dtype="float32", always_2d=False)
    return np.asarray(audio, dtype=np.float32), int(sample_rate)


def convert_to_mono(audio: np.ndarray) -> np.ndarray:
    """Average channels while preserving a one-dimensional waveform."""
    data = np.asarray(audio, dtype=np.float32)
    if data.ndim == 1:
        return data
    if data.ndim != 2:
        raise ValueError(f"Expected 1D or 2D audio, got shape {data.shape}")
    return data.mean(axis=1, dtype=np.float32)


def resample_audio(audio: np.ndarray, original_sr: int, target_sr: int) -> np.ndarray:
    """Resample using polyphase filtering."""
    if original_sr <= 0 or target_sr <= 0:
        raise ValueError("Sample rates must be positive")
    data = np.asarray(audio, dtype=np.float32)
    if original_sr == target_sr:
        return data.copy()
    factor = gcd(original_sr, target_sr)
    return resample_poly(data, target_sr // factor, original_sr // factor, axis=0).astype(np.float32)


def normalize_audio(audio: np.ndarray, peak: float = 0.99) -> np.ndarray:
    """Apply peak normalization only when clipping would otherwise occur."""
    data = np.asarray(audio, dtype=np.float32)
    maximum = float(np.max(np.abs(data))) if data.size else 0.0
    if not np.isfinite(maximum):
        raise ValueError("Audio contains NaN or infinite values")
    if maximum > 1.0:
        return (data * (peak / maximum)).astype(np.float32)
    return data.copy()


def save_audio(audio: np.ndarray, path: str | Path, sample_rate: int) -> None:
    """Write float WAV, creating parent directories and never touching raw input."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sf.write(destination, np.asarray(audio, dtype=np.float32), sample_rate, subtype="FLOAT")
