"""Configuration, reproducibility, paths, and leakage safeguards."""
from __future__ import annotations
import random
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import torch
import yaml

def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)

def resolve_path(value: str | Path, root: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path

def set_seed(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)

def verify_split_leakage(frames: dict[str, pd.DataFrame]) -> None:
    """Stop on source, hash, or (when available) speaker overlap."""
    names = list(frames)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            for column in ("source_file", "source_file_hash", "speaker_id"):
                if column not in frames[left] or column not in frames[right]: continue
                a = set(frames[left][column].dropna().astype(str)) - {"", "nan"}
                b = set(frames[right][column].dropna().astype(str)) - {"", "nan"}
                overlap = a & b
                if overlap:
                    raise ValueError(f"Leakage: {column} overlaps between {left} and {right} ({len(overlap)} values)")

def class_weights(labels: pd.Series) -> torch.Tensor:
    counts = labels.astype(int).value_counts()
    if set(counts.index) != {0, 1}: raise ValueError("Training data must contain labels 0 and 1")
    total = float(counts.sum())
    return torch.tensor([total / (2 * counts[0]), total / (2 * counts[1])], dtype=torch.float32)
