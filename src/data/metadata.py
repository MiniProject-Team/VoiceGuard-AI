"""Metadata schemas, hashing, duplicate detection, and summaries."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
import pandas as pd

PROCESSED_COLUMNS = ["segment_id", "file_path", "source_file", "split", "label", "label_name",
                     "speaker_id", "language", "source_dataset", "sample_rate", "channels",
                     "duration", "start_time", "end_time", "padding_applied", "augmentation",
                     "source_file_hash"]


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_processed_schema(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in PROCESSED_COLUMNS:
        if column not in result:
            result[column] = None
    return result[PROCESSED_COLUMNS]


def find_duplicates(frame: pd.DataFrame, hash_column: str = "source_file_hash") -> pd.DataFrame:
    if hash_column not in frame:
        return frame.iloc[0:0].copy()
    mask = frame[hash_column].notna() & frame[hash_column].duplicated(keep=False)
    return frame.loc[mask].sort_values(hash_column)


def dataset_summary(raw: pd.DataFrame, processed: pd.DataFrame) -> dict[str, Any]:
    file_counts = raw.get("label_name", pd.Series(dtype=str)).value_counts()
    segment_counts = processed.get("label_name", pd.Series(dtype=str)).value_counts()
    fake = int(segment_counts.get("fake", 0))
    return {"total_files": len(raw), "real_files": int(file_counts.get("real", 0)),
            "fake_files": int(file_counts.get("fake", 0)), "total_segments": len(processed),
            "real_segments": int(segment_counts.get("real", 0)), "fake_segments": fake,
            "real_fake_segment_ratio": (float(segment_counts.get("real", 0)) / fake if fake else None),
            "split_counts": processed.get("split", pd.Series(dtype=str)).value_counts().to_dict()}
