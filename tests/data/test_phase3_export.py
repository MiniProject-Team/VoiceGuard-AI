import json
from pathlib import Path

import numpy as np
import soundfile as sf

from src.data.phase3_export import existing_sample_ids, export_record
from src.data.sources.base import SourceRecord


def record(sample_id: str = "sample_001", label: int = 0, audio=None) -> SourceRecord:
    return SourceRecord(sample_id=sample_id, original_label="bonafide" if label == 0 else "spoof", voiceguard_label=label,
                        audio={"array": np.asarray(audio if audio is not None else np.ones(16000, dtype=np.float32) * .1), "sampling_rate": 8000},
                        source_dataset="InTheWild", source_split="train", speaker_id="Speaker One", language="english", reference="recording.wav")


def test_export_maps_labels_metadata_and_pcm16_wav(tmp_path: Path):
    metadata = tmp_path / "raw" / "phase3_metadata.jsonl"
    state, row = export_record(record(), tmp_path / "raw", metadata, set())
    assert state == "exported" and row is not None
    path = Path(row["export_path"])
    info = sf.info(path)
    assert "real/InTheWild/english/Speaker_One" in path.as_posix()
    assert info.samplerate == 16000 and info.channels == 1 and info.subtype == "PCM_16"
    saved = json.loads(metadata.read_text(encoding="utf-8"))
    assert saved["original_label"] == "bonafide" and saved["voiceguard_label"] == 0


def test_duplicate_resumability_and_dry_run_do_not_write(tmp_path: Path):
    metadata = tmp_path / "raw" / "phase3_metadata.jsonl"
    known = set()
    assert export_record(record(), tmp_path / "raw", metadata, known)[0] == "exported"
    assert export_record(record(), tmp_path / "raw", metadata, known)[0] == "duplicate"
    dry_metadata = tmp_path / "dry" / "phase3_metadata.jsonl"
    assert export_record(record("dry"), tmp_path / "dry", dry_metadata, set(), dry_run=True)[0] == "would_export"
    assert not dry_metadata.exists()
    assert existing_sample_ids(metadata) == {"sample_001"}


def test_invalid_audio_and_short_audio_are_rejected(tmp_path: Path):
    metadata = tmp_path / "phase3_metadata.jsonl"
    short = record("short", audio=np.ones(100, dtype=np.float32))
    assert export_record(short, tmp_path, metadata, set())[0] == "invalid_audio"
    invalid = record("invalid", audio=np.array([np.nan] * 8000, dtype=np.float32))
    assert export_record(invalid, tmp_path, metadata, set())[0] == "invalid_audio"
