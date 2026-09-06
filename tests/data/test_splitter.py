import pandas as pd
from src.data.splitter import split_dataset, verify_no_leakage

def _data():
    return pd.DataFrame([{"file_path": f"{label}_{i}.wav", "label": label} for label in [0, 1] for i in range(100)])

def test_deterministic_and_approximate_proportions():
    first, second = split_dataset(_data()), split_dataset(_data())
    assert first["split"].tolist() == second["split"].tolist()
    assert first["split"].value_counts().to_dict() == {"train": 140, "validation": 30, "test": 30}

def test_no_source_overlap_and_speaker_grouping():
    data = pd.DataFrame([{"file_path": f"{speaker}_{i}.wav", "speaker_id": speaker, "label": speaker % 2}
                         for speaker in range(20) for i in range(2)])
    result = split_dataset(data, group_column="speaker_id")
    assert result.groupby("speaker_id")["split"].nunique().max() == 1

def test_leakage_checker_rejects_source_and_hash_overlap():
    bad = pd.DataFrame({"source_file": ["a", "a"], "source_file_hash": ["x", "x"],
                        "split": ["train", "test"]})
    try:
        verify_no_leakage(bad)
    except ValueError as exc:
        assert "leakage" in str(exc).lower()
    else:
        raise AssertionError("Expected leakage detection")
