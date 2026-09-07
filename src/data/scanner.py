"""Recursive, label-aware raw audio discovery."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import pandas as pd

LOGGER = logging.getLogger(__name__)
SUPPORTED_EXTENSIONS = {".wav", ".flac", ".mp3", ".ogg"}
LABELS = {"real": 0, "fake": 1}


def iter_audio_files(raw_dir: Path) -> Iterator[Path]:
    """Yield supported files in stable order without loading audio."""
    for path in sorted(raw_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def infer_label(path: Path, raw_dir: Path) -> tuple[int, str] | None:
    """Infer label from the nearest real/fake directory below raw_dir."""
    try:
        parts = path.relative_to(raw_dir).parts[:-1]
    except ValueError:
        return None
    for part in reversed(parts):
        name = part.lower()
        if name in LABELS:
            return LABELS[name], name
    return None


def infer_provenance(path: Path, raw_dir: Path) -> dict[str, str | None]:
    """Read optional provenance from label/source/language/speaker folders.

    The supported intake layout is
    ``raw/<real|fake>/<source_dataset>/<language>/<speaker_id>/<file>``.
    Files directly under ``real`` or ``fake`` remain supported, but have no
    provenance metadata and therefore cannot satisfy the Phase 3 readiness gate.
    """
    try:
        parts = path.relative_to(raw_dir).parts[:-1]
    except ValueError:
        return {"source_dataset": None, "language": None, "speaker_id": None}
    label_index = next((index for index in range(len(parts) - 1, -1, -1) if parts[index].lower() in LABELS), None)
    values = parts[label_index + 1:] if label_index is not None else ()
    return {
        "source_dataset": values[0] if len(values) >= 1 else None,
        "language": values[1] if len(values) >= 2 else None,
        "speaker_id": values[2] if len(values) >= 3 else None,
    }


def scan_dataset(raw_dir: str | Path) -> pd.DataFrame:
    """Return one metadata row per supported, correctly labelled file."""
    root = Path(raw_dir)
    rows: list[dict[str, object]] = []
    for path in iter_audio_files(root):
        label = infer_label(path, root)
        if label is None:
            LOGGER.warning("Skipping audio outside a real/fake directory: %s", path)
            continue
        label_value, label_name = label
        rows.append({"file_path": path.as_posix(), "filename": path.name,
                     "label": label_value, "label_name": label_name,
                     "extension": path.suffix.lower(), **infer_provenance(path, root)})
    LOGGER.info("Discovered %d labelled audio files under %s", len(rows), root)
    return pd.DataFrame(rows, columns=["file_path", "filename", "label", "label_name", "extension", "source_dataset", "language", "speaker_id"])
