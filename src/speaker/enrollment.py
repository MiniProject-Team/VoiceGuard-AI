"""Multi-recording speaker enrollment and local template storage."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable
import numpy as np
from .embedding import normalize_embedding

def enroll_speaker(speaker_id: str, audio_paths: list[str | Path], extractor: Callable[[Path], np.ndarray],
                   output_dir: str | Path, model_metadata: dict[str, Any], minimum_reference_files: int = 2) -> dict[str, Any]:
    paths = [Path(path).resolve() for path in audio_paths]
    if len(paths) < minimum_reference_files: raise ValueError(f"At least {minimum_reference_files} reference files are required")
    missing = [str(path) for path in paths if not path.is_file()]
    if missing: raise FileNotFoundError(f"Missing enrollment files: {missing}")
    embeddings = [normalize_embedding(extractor(path)) for path in paths]
    dimensions = {item.shape for item in embeddings}
    if len(dimensions) != 1: raise ValueError("Enrollment embeddings have inconsistent dimensions")
    template = normalize_embedding(np.mean(np.stack(embeddings), axis=0)); destination = Path(output_dir); destination.mkdir(parents=True, exist_ok=True)
    np.save(destination / f"{speaker_id}.npy", template, allow_pickle=False)
    metadata = {"speaker_id": speaker_id, "number_of_reference_files": len(paths), "created_at": datetime.now(timezone.utc).isoformat(),
                "embedding_dimension": int(template.size), "reference_files": [str(path) for path in paths], **model_metadata}
    (destination / f"{speaker_id}.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata

def load_enrollment(speaker_id: str, embedding_dir: str | Path) -> tuple[np.ndarray, dict[str, Any]]:
    directory = Path(embedding_dir); vector, metadata = directory / f"{speaker_id}.npy", directory / f"{speaker_id}.json"
    if not vector.exists() or not metadata.exists(): raise KeyError(f"Speaker is not enrolled: {speaker_id}")
    return np.load(vector, allow_pickle=False), json.loads(metadata.read_text(encoding="utf-8"))

def verify_no_enrollment_test_overlap(enrollment_metadata: dict[str, Any], test_path: str | Path) -> None:
    target = Path(test_path).resolve()
    if target in {Path(path).resolve() for path in enrollment_metadata.get("reference_files", [])}:
        raise ValueError("Enrollment/test leakage: the exact recording is enrolled and tested")
