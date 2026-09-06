"""Audio integrity and quality checks."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import numpy as np
import soundfile as sf

from .audio_utils import load_audio


def validate_audio(path: str | Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate one file without modifying it; always return a report row."""
    cfg = config or {}
    row: dict[str, Any] = {"file_path": Path(path).as_posix(), "status": "INVALID", "reason": "",
                           "sample_rate": None, "channels": None, "duration": None,
                           "num_samples": None, "amplitude_min": None, "amplitude_max": None,
                           "silence_percentage": None}
    try:
        info = sf.info(Path(path))
        row.update(sample_rate=int(info.samplerate), channels=int(info.channels),
                   duration=float(info.duration), num_samples=int(info.frames))
        if info.frames <= 0:
            row["reason"] = "zero-length file"
            return row
        audio, _ = load_audio(path)
        if not np.all(np.isfinite(audio)):
            row["reason"] = "NaN or infinite samples"
            return row
        row["amplitude_min"] = float(audio.min())
        row["amplitude_max"] = float(audio.max())
        threshold = float(cfg.get("silence_threshold", 1e-4))
        silence_fraction = float(np.mean(np.abs(audio) <= threshold))
        row["silence_percentage"] = silence_fraction * 100.0
        warnings: list[str] = []
        if info.duration < float(cfg.get("minimum_duration_seconds", 0.1)):
            warnings.append("extremely short")
        supported = cfg.get("supported_sample_rates")
        if supported and info.samplerate not in supported:
            warnings.append("unsupported sample rate")
        if silence_fraction >= float(cfg.get("silent_fraction_warning", 0.99)):
            warnings.append("silent or near-silent")
        elif max(abs(row["amplitude_min"]), abs(row["amplitude_max"])) < float(cfg.get("low_peak_warning", .001)):
            warnings.append("very low volume")
        if cfg.get("warn_multiple_channels", True) and info.channels > 1:
            warnings.append("multiple channels")
        row["status"] = "WARNING" if warnings else "VALID"
        row["reason"] = "; ".join(warnings)
    except Exception as exc:  # backend errors vary by format
        row["reason"] = f"unreadable: {type(exc).__name__}: {exc}"
    return row
