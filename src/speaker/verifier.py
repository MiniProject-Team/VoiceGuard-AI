"""Phase 5-ready speaker verification interface; no risk scoring."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Callable
import numpy as np
from src.data.audio_utils import convert_to_mono, load_audio, resample_audio
from src.data.segmenter import segment_audio
from .embedding import normalize_embedding, quality_check
from .enrollment import load_enrollment
from .similarity import cosine_similarity

class SpeakerVerifier:
    def __init__(self, embedding_dir: str | Path, extractor_from_waveform: Callable[[np.ndarray, int], np.ndarray],
                 audio_config: dict[str, Any], threshold: float | None, aggregation: str = "mean"):
        self.embedding_dir, self.extractor, self.audio_config, self.threshold, self.aggregation = Path(embedding_dir), extractor_from_waveform, audio_config, threshold, aggregation
        if aggregation != "mean": raise ValueError("Initial implementation supports aggregation='mean'")
    def verify(self, speaker_id: str, audio_path: str | Path, allow_enrollment_recording: bool = False) -> dict[str, Any]:
        try: template, metadata = load_enrollment(speaker_id, self.embedding_dir)
        except KeyError as exc: return {"speaker_id": speaker_id, "similarity": None, "threshold": self.threshold, "verified": None, "status": "speaker_not_enrolled", "reason": str(exc)}
        path = Path(audio_path).resolve()
        if not allow_enrollment_recording and path in {Path(item).resolve() for item in metadata.get("reference_files", [])}:
            return {"speaker_id": speaker_id, "similarity": None, "threshold": self.threshold, "verified": None, "status": "leakage_rejected", "reason": "exact enrollment recording cannot be used as a verification trial"}
        try: audio, sr = load_audio(path)
        except Exception as exc: return {"speaker_id": speaker_id, "similarity": None, "threshold": self.threshold, "verified": None, "status": "invalid_audio", "reason": str(exc)}
        valid, reason = quality_check(audio, sr, self.audio_config)
        if not valid: return {"speaker_id": speaker_id, "similarity": None, "threshold": self.threshold, "verified": None, "status": "insufficient_audio" if reason.startswith("insufficient") else "invalid_audio", "reason": reason}
        mono = resample_audio(convert_to_mono(audio), sr, int(self.audio_config["sample_rate"])); target_sr = int(self.audio_config["sample_rate"])
        maximum = round(float(self.audio_config["max_duration_seconds"]) * target_sr); mono = mono[:maximum]
        windows = segment_audio(mono, target_sr, float(self.audio_config["window_duration_seconds"]), float(self.audio_config["window_hop_seconds"]), "pad")
        similarities = [cosine_similarity(template, normalize_embedding(self.extractor(window.audio, target_sr))) for window in windows]
        similarity = float(np.mean(similarities))
        if self.threshold is None: return {"speaker_id": speaker_id, "similarity": similarity, "threshold": None, "verified": None, "status": "threshold_not_calibrated", "reason": "Calibrate on validation trials before making a decision"}
        return {"speaker_id": speaker_id, "similarity": similarity, "threshold": self.threshold, "verified": similarity >= self.threshold, "status": "ok"}

def verify_speaker(speaker_id: str, audio_path: str | Path, verifier: SpeakerVerifier) -> dict[str, Any]:
    return verifier.verify(speaker_id, audio_path)
