from pathlib import Path

from src.data.scanner import scan_dataset


def test_scanner_preserves_structured_provenance(tmp_path: Path):
    target = tmp_path / "raw" / "real" / "common_voice" / "indian_english" / "speaker_001"
    target.mkdir(parents=True)
    (target / "sample.wav").write_bytes(b"placeholder")
    row = scan_dataset(tmp_path / "raw").iloc[0]
    assert row["label"] == 0
    assert row["source_dataset"] == "common_voice"
    assert row["language"] == "indian_english"
    assert row["speaker_id"] == "speaker_001"


def test_scanner_keeps_flat_layout_compatible_without_provenance(tmp_path: Path):
    target = tmp_path / "raw" / "fake"
    target.mkdir(parents=True)
    (target / "sample.wav").write_bytes(b"placeholder")
    row = scan_dataset(tmp_path / "raw").iloc[0]
    assert row["label"] == 1
    assert row[["source_dataset", "language", "speaker_id"]].isna().all()
