"""Safe local WAV export for Phase 3 public-dataset subsets."""
from __future__ import annotations

import hashlib
import io
import json
import re
from threading import Lock
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from .audio_utils import convert_to_mono, resample_audio
from .sources.base import SourceRecord

TARGET_SAMPLE_RATE = 16000
MIN_DURATION_SECONDS = 0.5
_EXPORT_LOCK = Lock()


def safe_component(value: str | None, fallback: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "").strip()).strip("._")
    return text[:96] or fallback


def existing_sample_ids(metadata_path: Path) -> set[str]:
    if not metadata_path.exists():
        return set()
    result: set[str] = set()
    for line in metadata_path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
            if isinstance(value, dict) and value.get("sample_id"):
                result.add(str(value["sample_id"]))
        except json.JSONDecodeError:
            continue
    return result


def decode_audio(value: Any) -> tuple[np.ndarray, int]:
    if isinstance(value, dict):
        if value.get("array") is not None and value.get("sampling_rate"):
            return np.asarray(value["array"], dtype=np.float32), int(value["sampling_rate"])
        if value.get("bytes") is not None:
            return sf.read(io.BytesIO(value["bytes"]), dtype="float32", always_2d=False)
        if value.get("path"):
            return sf.read(value["path"], dtype="float32", always_2d=False)
    raise ValueError("Source audio must expose decoded array/sampling_rate, bytes, or a readable path.")


def export_record(record: SourceRecord, output_root: Path, metadata_path: Path, known_ids: set[str], dry_run: bool = False) -> tuple[str, dict[str, Any] | None]:
    """Export one record or return a stable skip/rejection reason."""
    if record.voiceguard_label not in {0, 1}:
        return "invalid_label", None
    if record.sample_id in known_ids:
        return "duplicate", None
    try:
        audio_value = record.audio
        original_bytes = audio_value.get("bytes") if isinstance(audio_value, dict) else None
        if isinstance(audio_value, dict) and audio_value.get("url"):
            import requests
            response = requests.get(str(audio_value["url"]), timeout=60)
            response.raise_for_status()
            original_bytes = response.content
            audio_value = {"bytes": original_bytes}
        waveform, sample_rate = decode_audio(audio_value)
        waveform = convert_to_mono(waveform)
        if waveform.size == 0 or not np.all(np.isfinite(waveform)):
            return "invalid_audio", None
        if sample_rate <= 0:
            return "invalid_audio", None
        duration = float(waveform.size / sample_rate)
        if duration < MIN_DURATION_SECONDS:
            return "invalid_audio", None
        waveform = resample_audio(waveform, sample_rate, TARGET_SAMPLE_RATE)
        waveform = np.clip(waveform, -1.0, 1.0).astype(np.float32)
    except Exception:
        return "invalid_audio", None
    label_dir = "real" if record.voiceguard_label == 0 else "fake"
    dataset = safe_component(record.source_dataset, "unknown_source")
    language = safe_component(record.language, "unknown_language")
    speaker = safe_component(record.speaker_id, f"source_{record.sample_id[:12]}")
    destination = output_root / label_dir / dataset / language / speaker / f"{safe_component(record.sample_id, 'sample')}.wav"
    metadata = {
        "sample_id": record.sample_id,
        "source_dataset": record.source_dataset,
        "source_split": record.source_split,
        "original_label": record.original_label,
        "voiceguard_label": record.voiceguard_label,
        "speaker_id": speaker,
        "language": language,
        "generator_family": record.generator_family,
        "original_path_or_reference": record.reference,
        "duration_seconds": duration,
        "sample_rate": TARGET_SAMPLE_RATE,
        "export_path": destination.as_posix(),
        "longer_than_training_window": duration > 5.0,
        "source_metadata": record.metadata,
    }
    if dry_run:
        return "would_export", metadata
    # Concurrent bounded downloads may finish together.  Keep the observable
    # export (destination, originals, metadata and in-memory IDs) atomic.
    with _EXPORT_LOCK:
        if record.sample_id in known_ids or destination.exists():
            return "duplicate", None
        destination.parent.mkdir(parents=True, exist_ok=True)
        sf.write(destination, waveform, TARGET_SAMPLE_RATE, subtype="PCM_16")
        if isinstance(original_bytes, bytes):
            extension = safe_component(str(record.metadata.get("original_extension") or "bin"), "bin")
            original_path = output_root.parent / "source_originals" / dataset / f"{safe_component(record.sample_id, 'sample')}.{extension}"
            original_path.parent.mkdir(parents=True, exist_ok=True)
            original_path.write_bytes(original_bytes)
            metadata["source_original_path"] = original_path.as_posix()
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with metadata_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(metadata, ensure_ascii=False, sort_keys=True) + "\n")
        known_ids.add(record.sample_id)
    return "exported", metadata


def source_group(record: SourceRecord) -> str:
    value = record.speaker_id or record.reference or record.sample_id
    return hashlib.sha256(f"{record.source_dataset}:{value}".encode("utf-8")).hexdigest()[:12]
