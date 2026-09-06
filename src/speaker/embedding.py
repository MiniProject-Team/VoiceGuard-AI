"""SpeechBrain ECAPA loading, audio quality checking, extraction, and caching."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any
import numpy as np
import torch
from src.data.audio_utils import convert_to_mono, load_audio, resample_audio

def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    value = np.asarray(embedding, dtype=np.float32).reshape(-1); norm = float(np.linalg.norm(value))
    if not np.isfinite(norm) or norm == 0: raise ValueError("Cannot normalize an invalid or zero embedding")
    return (value / norm).astype(np.float32)

def load_speaker_model(model_name: str, device: str | None = None, savedir: str | Path | None = None) -> Any:
    from speechbrain.inference.speaker import EncoderClassifier
    from speechbrain.utils.fetching import LocalStrategy
    run_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    return EncoderClassifier.from_hparams(source=model_name, savedir=str(savedir) if savedir else None,
                                          run_opts={"device": run_device}, local_strategy=LocalStrategy.COPY)

def quality_check(audio: np.ndarray, sample_rate: int, config: dict[str, Any]) -> tuple[bool, str]:
    if audio.size == 0 or not np.all(np.isfinite(audio)): return False, "empty or invalid samples"
    duration = audio.shape[0] / sample_rate
    if duration < float(config["minimum_duration_seconds"]): return False, f"insufficient audio: {duration:.3f}s"
    mono = convert_to_mono(audio); silence = float(np.mean(np.abs(mono) <= 1e-4))
    if silence > float(config.get("maximum_silence_fraction", .95)): return False, "excessive silence"
    clipping = float(np.mean(np.abs(mono) >= .999))
    if clipping > float(config.get("clipping_fraction_limit", .05)): return False, "excessive clipping"
    return True, "ok"

def extract_embedding_from_waveform(waveform: np.ndarray, sample_rate: int, model: Any,
                                    target_sample_rate: int = 16000, normalize: bool = True) -> np.ndarray:
    audio = convert_to_mono(waveform); audio = resample_audio(audio, sample_rate, target_sample_rate)
    tensor = torch.from_numpy(audio).float().unsqueeze(0)
    device = next(model.mods.parameters()).device if hasattr(model, "mods") else torch.device("cpu")
    with torch.no_grad(): encoded = model.encode_batch(tensor.to(device))
    embedding = encoded.detach().cpu().numpy().reshape(-1).astype(np.float32)
    return normalize_embedding(embedding) if normalize else embedding

def _cache_key(path: Path, model_name: str, settings: dict[str, Any], preprocessing_version: str) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): digest.update(chunk)
    digest.update(model_name.encode()); digest.update(json.dumps(settings, sort_keys=True).encode()); digest.update(preprocessing_version.encode()); return digest.hexdigest()

def extract_embedding(audio_path: str | Path, model: Any, model_name: str, audio_config: dict[str, Any],
                      cache_dir: str | Path | None = None, preprocessing_version: str = "phase4-v1",
                      normalize: bool = True) -> np.ndarray:
    path = Path(audio_path); audio, sr = load_audio(path); valid, reason = quality_check(audio, sr, audio_config)
    if not valid: raise ValueError(f"Unusable audio {path}: {reason}")
    key = _cache_key(path, model_name, audio_config, preprocessing_version); cache = Path(cache_dir) / f"{key}.npy" if cache_dir else None
    if cache and cache.exists(): return np.load(cache, allow_pickle=False)
    result = extract_embedding_from_waveform(audio, sr, model, int(audio_config["sample_rate"]), normalize)
    if cache: cache.parent.mkdir(parents=True, exist_ok=True); np.save(cache, result, allow_pickle=False)
    return result
