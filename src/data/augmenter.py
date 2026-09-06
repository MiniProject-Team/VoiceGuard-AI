"""Conservative, optional waveform augmentation."""
from __future__ import annotations

from typing import Any
import numpy as np
from scipy.signal import butter, sosfilt


def add_background_noise(audio: np.ndarray, rng: np.random.Generator, snr_db: float = 30.0) -> np.ndarray:
    signal_rms = float(np.sqrt(np.mean(np.square(audio)))) if audio.size else 0.0
    if signal_rms == 0:
        return audio.copy()
    noise = rng.normal(0, signal_rms / (10 ** (snr_db / 20)), audio.shape)
    return (audio + noise).astype(np.float32)


def vary_gain(audio: np.ndarray, rng: np.random.Generator, max_db: float = 3.0) -> np.ndarray:
    return (audio * 10 ** (rng.uniform(-max_db, max_db) / 20)).astype(np.float32)


def simulate_telephone_audio(audio: np.ndarray, sample_rate: int) -> np.ndarray:
    """Conservatively band-limit to 300-3400 Hz; this is not a codec emulator."""
    if sample_rate < 8000:
        return np.asarray(audio, dtype=np.float32).copy()
    sos = butter(4, [300, min(3400, sample_rate * .45)], btype="bandpass", fs=sample_rate, output="sos")
    return sosfilt(sos, audio).astype(np.float32)


def augment_audio(audio: np.ndarray, sample_rate: int, config: dict[str, Any],
                  rng: np.random.Generator) -> tuple[np.ndarray, str]:
    """Apply configured mild augmentations and return a provenance string."""
    if not config.get("enabled", False):
        return audio.copy(), "none"
    result, applied = audio.copy(), []
    if rng.random() < float(config.get("noise_probability", 0)):
        result, applied = add_background_noise(result, rng), applied + ["noise"]
    if rng.random() < float(config.get("gain_probability", 0)):
        result, applied = vary_gain(result, rng), applied + ["gain"]
    if rng.random() < float(config.get("telephone_probability", 0)):
        result, applied = simulate_telephone_audio(result, sample_rate), applied + ["telephone_bandlimit"]
    # Speed/pitch fields are accepted for experiment compatibility, but intentionally
    # deferred: naive transforms can erase the artifacts the detector must learn.
    return np.clip(result, -1, 1).astype(np.float32), "+".join(applied) or "none"
