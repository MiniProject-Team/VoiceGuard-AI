import json
import io
from pathlib import Path

import numpy as np
import soundfile as sf

from src.data.phase3_export import export_record
from src.data.sources.asvspoof import ASVspoofSource


def test_asvspoof_label_mapping_is_exact_and_not_inferred():
    assert ASVspoofSource._classify_label("bonafide") == 0
    assert ASVspoofSource._classify_label("spoof") == 1
    assert ASVspoofSource._classify_label("deepfake") is None
    assert ASVspoofSource._classify_label("unknown") is None


def test_asvspoof_record_preserves_protocol_provenance_and_unknown_attack():
    source = ASVspoofSource()
    source.label_mapping, source.original_labels, source.total_rows = {0: 0, 1: 1}, {0: "bonafide", 1: "spoof"}, 1
    record = source._record_from_row({
        "path": "LA_E_1234567.flac",
        "label": 1,
        "notes": json.dumps({"utterance_id": "LA_E_1234567", "speaker_id": "LA_0012", "subset": "eval"}),
    }, {"bytes": b"audio-bytes"})
    assert record.source_dataset == "ASVspoof"
    assert record.source_split == "test"
    assert record.voiceguard_label == 1 and record.original_label == "spoof"
    assert record.speaker_id == "LA_0012"
    assert record.generator_family == "unknown"
    assert record.metadata["track"] == ASVspoofSource.track


def test_asvspoof_export_uses_separate_folder_and_resumes_by_stable_id(tmp_path: Path):
    source = ASVspoofSource()
    source.label_mapping, source.original_labels, source.total_rows = {0: 0, 1: 1}, {0: "bonafide", 1: "spoof"}, 1
    original = io.BytesIO()
    sf.write(original, np.ones(16000, dtype=np.float32) * 0.1, 16000, format="FLAC")
    record = source._record_from_row({
        "path": "LA_E_7654321.flac", "label": 0,
        "notes": json.dumps({"utterance_id": "LA_E_7654321", "speaker_id": "LA_0013", "subset": "eval"}),
    }, {"bytes": original.getvalue()})
    metadata_path = tmp_path / "raw" / "phase3_metadata.jsonl"
    known_ids: set[str] = set()
    state, metadata = export_record(record, tmp_path / "raw", metadata_path, known_ids)
    assert state == "exported" and metadata is not None
    assert "/real/ASVspoof/english/LA_0013/" in metadata["export_path"]
    assert Path(metadata["source_original_path"]).is_file()
    assert export_record(record, tmp_path / "raw", metadata_path, known_ids)[0] == "duplicate"
