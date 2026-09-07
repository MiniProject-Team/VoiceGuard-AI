"""Deterministic grouped and stratified dataset splitting."""
from __future__ import annotations

import hashlib
import pandas as pd


def _rank(seed: int, value: object) -> str:
    return hashlib.sha256(f"{seed}:{value}".encode()).hexdigest()


def _split_counts(n: int, fractions: tuple[float, float, float]) -> tuple[int, int, int]:
    """Allocate counts deterministically, keeping nonzero splits populated when possible."""
    positive = [index for index, value in enumerate(fractions) if value > 0]
    counts = [0, 0, 0]
    if n >= len(positive):
        for index in positive:
            counts[index] = 1
        remaining = n - len(positive)
        targets = [max(0.0, n * fractions[index] - counts[index]) for index in range(3)]
    else:
        remaining, targets = n, list(fractions)
    total = sum(targets)
    quotas = [remaining * value / total if total else 0 for value in targets]
    floors = [int(value) for value in quotas]
    counts = [counts[index] + floors[index] for index in range(3)]
    for index in sorted(range(3), key=lambda item: (quotas[item] - floors[item], fractions[item]), reverse=True)[:n - sum(counts)]:
        counts[index] += 1
    return counts[0], counts[1], counts[2]


def split_dataset(metadata: pd.DataFrame, train: float = .70, validation: float = .15,
                  test: float = .15, random_seed: int = 42,
                  group_column: str | None = None) -> pd.DataFrame:
    """Assign groups to splits, stratified by label where possible."""
    if abs(train + validation + test - 1.0) > 1e-8 or min(train, validation, test) < 0:
        raise ValueError("Split fractions must be non-negative and sum to 1")
    result = metadata.copy()
    if result.empty:
        result["split"] = pd.Series(dtype="object")
        return result
    group = group_column if group_column and group_column in result and result[group_column].notna().all() else "file_path"
    assignments: dict[object, str] = {}
    grouped = result.groupby(["label", group], dropna=False).size().reset_index(name="_count")
    # When a speaker/group contains both classes, assigning it once per label
    # would overwrite an earlier choice and leak that speaker across splits.
    # Allocate mixed-label groups once while greedily balancing class totals.
    mixed_groups = grouped.groupby(group, dropna=False)["label"].nunique().max() > 1
    if mixed_groups:
        # Speaker groups with both labels cannot be independently stratified
        # without leakage. Allocate whole groups deterministically by the same
        # requested split fractions; downstream readiness reports the resulting
        # class counts for review.
        keys = sorted(grouped[group].unique().tolist(), key=lambda value: _rank(random_seed, value))
        n_train, n_validation, _ = _split_counts(len(keys), (train, validation, test))
        for index, key in enumerate(keys):
            assignments[key] = "train" if index < n_train else ("validation" if index < n_train + n_validation else "test")
    else:
        for _, label_groups in grouped.groupby("label"):
            keys = sorted(label_groups[group].tolist(), key=lambda value: _rank(random_seed, value))
            n = len(keys)
            n_train, n_validation, _ = _split_counts(n, (train, validation, test))
            for index, key in enumerate(keys):
                assignments[key] = "train" if index < n_train else ("validation" if index < n_train + n_validation else "test")
    result["split"] = result[group].map(assignments)
    return result


def verify_no_leakage(metadata: pd.DataFrame) -> None:
    """Raise ValueError if a source, speaker, or identical hash crosses splits."""
    if metadata.empty:
        return
    problems: list[str] = []
    for column in ("source_file", "file_path", "speaker_id"):
        if column not in metadata:
            continue
        subset = metadata
        if column == "speaker_id":
            subset = metadata[metadata[column].notna() & metadata[column].astype(str).str.strip().ne("")]
            if subset.empty:
                continue
        if subset.groupby(column, dropna=False)["split"].nunique().max() > 1:
            problems.append(f"{column} appears in multiple splits")
            break
    if "source_file_hash" in metadata:
        hashes = metadata.dropna(subset=["source_file_hash"])
        if not hashes.empty and hashes.groupby("source_file_hash")["split"].nunique().max() > 1:
            problems.append("duplicate hashes appear in multiple splits")
    if problems:
        raise ValueError("Dataset leakage detected: " + "; ".join(problems))
