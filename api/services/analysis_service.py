from __future__ import annotations
import asyncio, io, wave
from dataclasses import dataclass
from time import perf_counter
import numpy as np
import soundfile as sf
from src.realtime.alerts import AlertManager
from src.realtime.segmenter import RealtimeSegment
from .session_service import InvalidSessionState, SessionService
from security.policy import enforce_fail_safe
from security.privacy import retained_assessment
from security.input_validation import validate_upload_header

class AudioError(ValueError):
    def __init__(self, code: str, message: str): super().__init__(message); self.code = code
class ModelUnavailable(RuntimeError): pass

@dataclass
class AnalysisMetrics:
    completed: int = 0; errors: int = 0; alerts: int = 0; total_latency: float = 0.0

class AnalysisService:
    def __init__(self, processor, sessions: SessionService, config: dict):
        self.processor, self.sessions, self.config = processor, sessions, config
        self._inference_lock = asyncio.Lock(); self._slots = asyncio.Semaphore(int(config["runtime"]["max_pending_audio_chunks"])); self.metrics = AnalysisMetrics(); self._alerts: dict[str, AlertManager] = {}
    def decode_file(self, data: bytes, filename: str | None) -> np.ndarray:
        maximum = int(float(self.config["audio"]["max_file_size_mb"]) * 1024 * 1024)
        if not data: raise AudioError("INVALID_AUDIO", "Audio file is empty.")
        if len(data) > maximum: raise AudioError("AUDIO_TOO_LARGE", "Audio exceeds the configured size limit.")
        suffix = (filename or "").rsplit(".", 1)[-1].lower() if "." in (filename or "") else ""
        if suffix not in self.config["audio"]["allowed_formats"]: raise AudioError("UNSUPPORTED_AUDIO_FORMAT", "Supported formats are WAV and FLAC.")
        try: validate_upload_header(data,suffix)
        except ValueError as exc: raise AudioError("INVALID_AUDIO",str(exc)) from exc
        try: audio, rate = sf.read(io.BytesIO(data), dtype="float32", always_2d=True)
        except Exception as exc: raise AudioError("INVALID_AUDIO", "Audio file is corrupt or unreadable.") from exc
        if audio.shape[1] != int(self.config["audio"]["channels"]): raise AudioError("INVALID_AUDIO", "Audio must be mono.")
        if rate != int(self.config["audio"]["sample_rate"]): raise AudioError("INVALID_AUDIO", "Audio sample rate must be 16 kHz.")
        if len(audio) / rate > float(self.config["audio"]["max_duration_seconds"]): raise AudioError("AUDIO_TOO_LONG", "Audio exceeds the configured duration limit.")
        return audio[:, 0]
    def decode_pcm(self, data: bytes) -> np.ndarray:
        if not data: raise AudioError("INVALID_AUDIO", "Audio frame is empty.")
        if len(data) > int(self.config["audio"]["max_chunk_size_bytes"]): raise AudioError("AUDIO_TOO_LARGE", "Audio frame exceeds the configured chunk limit.")
        if len(data) % 2: raise AudioError("INVALID_AUDIO", "PCM16 audio must contain complete 16-bit samples.")
        duration = len(data) / 2 / int(self.config["audio"]["sample_rate"])
        if duration > float(self.config["audio"]["max_duration_seconds"]): raise AudioError("AUDIO_TOO_LONG", "Audio frame exceeds the configured duration limit.")
        return np.frombuffer(data, dtype="<i2").astype(np.float32) / 32768.0
    async def analyze(self, session_id: str, audio: np.ndarray) -> dict:
        session = await self.sessions.get(session_id)
        if session.status != "active": raise InvalidSessionState("Audio analysis requires an active session.")
        try: await asyncio.wait_for(self._slots.acquire(), timeout=0.001)
        except TimeoutError: raise AudioError("SERVER_BUSY", "The analysis queue is full.")
        started = perf_counter()
        try:
            segment_id = len(session.results) + 1
            segment = RealtimeSegment(session_id, segment_id, 0.0, len(audio) / int(self.config["audio"]["sample_rate"]), audio, 1.0)
            async with self._inference_lock:
                raw = await asyncio.to_thread(self.processor.process, segment, session.speaker_id, session.context)
            risk = raw["risk"]
            combined=enforce_fail_safe({**raw,**risk})
            result = {"session_id":session_id,"segment_id": segment_id,"timestamp":__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),"synthetic_probability": raw.get("synthetic_probability"), "synthetic_detection_status": raw.get("synthetic_detection_status", "unavailable"), "speaker_similarity": raw.get("speaker_similarity"), "speaker_verified": raw.get("speaker_verified"), "speaker_verification_status": raw.get("speaker_verification_status", "unavailable"), "risk_score": combined["risk_score"], "risk_level": combined["risk_level"], "decision": combined["decision"], "recommended_action": combined["recommended_action"], "reasons": combined.get("reasons", []),"engine_version":risk.get("engine_version"),"config_version":risk.get("configuration_version"),"config_hash":self.config.get("config_hash"),"model_versions":self.config.get("model_versions",{})}
            manager = self._alerts.setdefault(session_id, AlertManager(True, 30, "HIGH")); alert = manager.consider({**result, "session_id": session_id})
            result["alert_event"] = alert; await self.sessions.add_result(session_id, retained_assessment(result))
            elapsed = perf_counter() - started; self.metrics.completed += 1; self.metrics.total_latency += elapsed; self.metrics.alerts += int(alert is not None)
            if hasattr(self,"monitoring"):self.monitoring.record(latency=elapsed,rtf=elapsed/max(segment.end_time,1e-9),synthetic=result.get("synthetic_probability"),speaker=result.get("speaker_similarity"),risk=result.get("risk_score"),level=result.get("risk_level","UNKNOWN"),alert=alert is not None,degraded=combined.get("status")=="SYSTEM_DEGRADED")
            return result
        except (AudioError, InvalidSessionState): raise
        except Exception as exc:
            self.metrics.errors += 1; raise RuntimeError("Audio analysis could not be completed.") from exc
        finally: self._slots.release()
