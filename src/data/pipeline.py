"""End-to-end Phase 2 dataset pipeline."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

from .audio_utils import convert_to_mono, load_audio, normalize_audio, resample_audio, save_audio
from .augmenter import augment_audio
from .metadata import dataset_summary, ensure_processed_schema, find_duplicates, sha256_file
from .scanner import scan_dataset
from .segmenter import segment_audio
from .splitter import split_dataset, verify_no_leakage
from .validator import validate_audio

LOGGER = logging.getLogger(__name__)


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _resolve(path: str, project_root: Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else project_root / candidate


def run_pipeline(config_path: str | Path, dry_run: bool = False) -> dict[str, Any]:
    """Scan, validate, safely split, standardize and segment a dataset."""
    config_path = Path(config_path).resolve()
    root = config_path.parent.parent
    cfg = load_config(config_path)
    dataset_cfg = cfg["dataset"]
    raw_dir = _resolve(dataset_cfg["raw_dir"], root)
    metadata_dir = _resolve(dataset_cfg["metadata_dir"], root)
    processed_dir = _resolve(dataset_cfg["processed_dir"], root)
    reports_dir = _resolve(dataset_cfg.get("reports_dir", "reports"), root)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    raw = scan_dataset(raw_dir)
    raw.to_csv(metadata_dir / "raw_metadata.csv", index=False)
    validation_rows = [validate_audio(path, cfg.get("validation")) for path in tqdm(raw["file_path"], desc="Validating")]
    validation_columns = ["file_path", "status", "reason", "sample_rate", "channels", "duration",
                          "num_samples", "amplitude_min", "amplitude_max", "silence_percentage"]
    validation = pd.DataFrame(validation_rows, columns=validation_columns)
    validation.to_csv(metadata_dir / "validation_report.csv", index=False)
    combined = raw.merge(validation, on="file_path", how="left")
    usable = combined[combined["status"].isin(["VALID", "WARNING"])].copy()
    hashes: list[str | None] = []
    for path in tqdm(usable["file_path"], desc="Hashing"):
        try:
            hashes.append(sha256_file(path))
        except OSError as exc:
            LOGGER.error("Hash failed for %s: %s", path, exc)
            hashes.append(None)
    usable["source_file_hash"] = hashes
    split_cfg = cfg["split"]
    # Hash grouping keeps byte-identical copies together. Complete speaker metadata
    # takes precedence; duplicate-hash leakage is then caught by the mandatory audit.
    group_column = ("speaker_id" if "speaker_id" in usable and usable["speaker_id"].notna().all()
                    else "source_file_hash")
    usable = split_dataset(usable, split_cfg["train"], split_cfg["validation"], split_cfg["test"],
                           split_cfg["random_seed"], group_column)
    verify_no_leakage(usable.rename(columns={"file_path": "source_file"}))
    usable.to_csv(metadata_dir / "file_splits.csv", index=False)
    duplicates = find_duplicates(usable)
    duplicates.to_csv(metadata_dir / "duplicates.csv", index=False)

    if dry_run:
        summary = dataset_summary(raw, pd.DataFrame())
        summary.update(valid_files=int((validation["status"] == "VALID").sum()) if not validation.empty else 0,
                       warnings=int((validation["status"] == "WARNING").sum()) if not validation.empty else 0,
                       invalid_files=int((validation["status"] == "INVALID").sum()) if not validation.empty else 0,
                       possible_duplicate_files=len(duplicates), processing_failures=0, dry_run=True)
        (reports_dir / "dataset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        LOGGER.info("Dry run complete: %d usable; Invalid: %d; Warnings: %d",
                    len(usable), summary["invalid_files"], summary["warnings"])
        return summary

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    audio_cfg, segment_cfg = cfg["audio"], cfg["segmentation"]
    rng = np.random.default_rng(split_cfg["random_seed"])
    for record in tqdm(usable.to_dict("records"), desc="Processing"):
        try:
            audio, sr = load_audio(record["file_path"])
            audio = convert_to_mono(audio)
            audio = resample_audio(audio, sr, int(audio_cfg["sample_rate"]))
            if audio_cfg.get("normalize", True):
                audio = normalize_audio(audio)
            source_stem = record["source_file_hash"][:12]
            segments = segment_audio(audio, int(audio_cfg["sample_rate"]),
                                     float(segment_cfg["duration_seconds"]),
                                     float(segment_cfg["hop_seconds"]), segment_cfg["short_audio_policy"])
            for segment in segments:
                segment_id = f"{record['label_name']}_{source_stem}_{segment.index:04d}"
                output = processed_dir / record["split"] / record["label_name"] / f"{segment_id}.wav"
                waveform, augmentation = (augment_audio(segment.audio, int(audio_cfg["sample_rate"]), cfg["augmentation"], rng)
                                            if record["split"] == "train" else (segment.audio, "none"))
                save_audio(waveform, output, int(audio_cfg["sample_rate"]))
                rows.append({"segment_id": segment_id, "file_path": output.as_posix(),
                             "source_file": record["file_path"], "split": record["split"],
                             "label": record["label"], "label_name": record["label_name"],
                             "speaker_id": record.get("speaker_id"), "language": record.get("language"),
                             "source_dataset": record.get("source_dataset"),
                             "sample_rate": int(audio_cfg["sample_rate"]), "channels": 1,
                             "duration": segment.duration, "start_time": segment.start_time,
                             "end_time": segment.end_time, "padding_applied": segment.padding_applied,
                             "augmentation": augmentation, "source_file_hash": record["source_file_hash"]})
        except Exception as exc:
            LOGGER.exception("Failed processing %s", record["file_path"])
            errors.append({"file_path": record["file_path"], "error": f"{type(exc).__name__}: {exc}"})
    processed = ensure_processed_schema(pd.DataFrame(rows))
    verify_no_leakage(processed)
    processed.to_csv(metadata_dir / "processed_metadata.csv", index=False)
    for split in ("train", "validation", "test"):
        processed[processed["split"] == split].to_csv(metadata_dir / f"{split}.csv", index=False)
    pd.DataFrame(errors, columns=["file_path", "error"]).to_csv(metadata_dir / "processing_errors.csv", index=False)
    summary = dataset_summary(raw, processed)
    summary.update(valid_files=int((validation["status"] == "VALID").sum()) if not validation.empty else 0,
                   warnings=int((validation["status"] == "WARNING").sum()) if not validation.empty else 0,
                   invalid_files=int((validation["status"] == "INVALID").sum()) if not validation.empty else 0,
                   possible_duplicate_files=len(duplicates), processing_failures=len(errors), dry_run=dry_run)
    (reports_dir / "dataset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    LOGGER.info("Successfully processed: %d; Failed: %d; Warnings: %d", len(usable) - len(errors), len(errors), summary["warnings"])
    return summary
