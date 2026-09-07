"""Dataset and artifact safety gates for Phase 3 training and serving."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

MINIMUM_SAMPLES_PER_CLASS = 100
MINIMUM_TOTAL_SAMPLES = 400
MINIMUM_SOURCES_PER_CLASS = 2


@dataclass(frozen=True)
class DatasetReadiness:
    ready: bool
    reasons: list[str]
    counts: dict[str, int]


def assess_training_frames(frames: dict[str, pd.DataFrame]) -> DatasetReadiness:
    """Return a conservative readiness decision without changing source audio."""
    train = frames.get("train", pd.DataFrame())
    reasons: list[str] = []
    counts = {"train": len(train), "validation": len(frames.get("validation", [])), "test": len(frames.get("test", []))}
    if "label" not in train:
        return DatasetReadiness(False, ["training metadata has no label column"], counts)
    label_counts = train["label"].value_counts().to_dict()
    real, synthetic = int(label_counts.get(0, 0)), int(label_counts.get(1, 0))
    counts.update({"real_train": real, "synthetic_train": synthetic, "total": sum(counts.values())})
    if real < MINIMUM_SAMPLES_PER_CLASS:
        reasons.append(f"need at least {MINIMUM_SAMPLES_PER_CLASS} REAL training samples; found {real}")
    if synthetic < MINIMUM_SAMPLES_PER_CLASS:
        reasons.append(f"need at least {MINIMUM_SAMPLES_PER_CLASS} SYNTHETIC training samples; found {synthetic}")
    if counts["total"] < MINIMUM_TOTAL_SAMPLES:
        reasons.append(f"need at least {MINIMUM_TOTAL_SAMPLES} labelled samples across splits; found {counts['total']}")
    for label, name in ((0, "REAL"), (1, "SYNTHETIC")):
        subset = train[train["label"] == label]
        column = "source_dataset" if "source_dataset" in subset else None
        sources = set(subset[column].dropna().astype(str)) - {"", "nan"} if column else set()
        if len(sources) < MINIMUM_SOURCES_PER_CLASS:
            reasons.append(f"need at least {MINIMUM_SOURCES_PER_CLASS} documented synthesis/source datasets for {name}; found {len(sources)}")
    for split, frame in frames.items():
        labels = set(frame.get("label", pd.Series(dtype=int)).dropna().astype(int))
        if labels != {0, 1}:
            reasons.append(f"{split} split must contain both labels 0=REAL and 1=SYNTHETIC")
    return DatasetReadiness(not reasons, reasons, counts)


def reject_debug_or_random_artifact(training_config: dict[str, Any], model_info: dict[str, Any] | None = None) -> None:
    """Prevent debug/random checkpoints from being mistaken for a detector."""
    model_info = model_info or {}
    candidates = [
        str(training_config.get("model", {}).get("name", "")),
        str(training_config.get("model", {}).get("debug_name", "")),
        str(model_info.get("base_model", "")),
    ]
    if training_config.get("training", {}).get("debug_mode") or model_info.get("debug_mode"):
        raise ValueError("Debug Phase 3 artifacts are not eligible for production inference or registration.")
    if any("tiny-random" in value.lower() or "hf-internal-testing" in value.lower() for value in candidates):
        raise ValueError("Random/testing Hugging Face backbones are not eligible for production inference or registration.")
