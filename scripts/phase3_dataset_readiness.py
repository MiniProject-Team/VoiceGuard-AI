"""Generate an evidence-based Phase 3 dataset-readiness report."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models.readiness import assess_training_frames


def _values(frame: pd.DataFrame, column: str) -> list[str]:
    if column not in frame:
        return []
    return sorted({str(value) for value in frame[column].dropna() if str(value).strip() and str(value).lower() != "nan"})


def main() -> int:
    metadata = ROOT / "data" / "metadata"
    frames = {name: pd.read_csv(metadata / f"{name}.csv") for name in ("train", "validation", "test") if (metadata / f"{name}.csv").exists()}
    raw = pd.read_csv(metadata / "raw_metadata.csv") if (metadata / "raw_metadata.csv").exists() else pd.DataFrame()
    readiness = assess_training_frames(frames)
    all_rows = pd.concat(list(frames.values()), ignore_index=True) if frames else pd.DataFrame()
    report = {
        "status": "READY" if readiness.ready else "DATASET_INSUFFICIENT",
        "requirements": {"minimum_samples_per_class": 100, "minimum_total_samples": 400, "minimum_documented_sources_per_class": 2},
        "counts": readiness.counts,
        "raw_source_file_counts": {"real": int((raw.get("label", pd.Series(dtype=int)) == 0).sum()), "synthetic": int((raw.get("label", pd.Series(dtype=int)) == 1).sum())},
        "split_class_counts": {name: {str(key): int(value) for key, value in frame["label"].value_counts().to_dict().items()} for name, frame in frames.items()},
        "languages": _values(all_rows, "language"),
        "speakers": _values(all_rows, "speaker_id"),
        "source_datasets": _values(all_rows, "source_dataset"),
        "duration_seconds": {"total": float(all_rows.get("duration", pd.Series(dtype=float)).sum()), "minimum": float(all_rows.get("duration", pd.Series(dtype=float)).min()) if "duration" in all_rows and not all_rows.empty else None, "maximum": float(all_rows.get("duration", pd.Series(dtype=float)).max()) if "duration" in all_rows and not all_rows.empty else None},
        "duplicate_rows_reported": int(len(pd.read_csv(metadata / "duplicates.csv"))) if (metadata / "duplicates.csv").exists() else None,
        "missing_requirements": readiness.reasons,
        "label_mapping": {"0": "REAL", "1": "SYNTHETIC"},
    }
    output = ROOT / "reports" / "phase3"
    output.mkdir(parents=True, exist_ok=True)
    (output / "dataset_readiness.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Phase 3 dataset readiness", "", f"**{report['status']}**", "", "## Observed data", "", f"- Raw source files: {report['raw_source_file_counts']['real']} REAL, {report['raw_source_file_counts']['synthetic']} SYNTHETIC.", f"- Split rows: train {report['counts'].get('train', 0)}, validation {report['counts'].get('validation', 0)}, test {report['counts'].get('test', 0)}.", f"- Languages: {', '.join(report['languages']) or 'not documented'}.", f"- Speakers: {', '.join(report['speakers']) or 'not documented'}.", f"- Source datasets: {', '.join(report['source_datasets']) or 'not documented'}.", "", "## Decision", ""]
    if readiness.ready:
        lines.append("Dataset passes the configured conservative readiness gate. Training may proceed after split/leakage checks.")
    else:
        lines.extend(["Training is blocked. The current data cannot support held-out performance claims:", "", *[f"- {reason}" for reason in readiness.reasons]])
    (output / "dataset_readiness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if readiness.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
