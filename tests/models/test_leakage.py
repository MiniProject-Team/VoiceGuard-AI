import pandas as pd, pytest
from src.models.utils import verify_split_leakage

def test_overlapping_sources_detected():
    frames = {"train": pd.DataFrame({"source_file": ["same.wav"]}), "test": pd.DataFrame({"source_file": ["same.wav"]})}
    with pytest.raises(ValueError, match="Leakage"): verify_split_leakage(frames)
