from pathlib import Path
import numpy as np
import pandas as pd
import soundfile as sf
import yaml

from src.data.pipeline import run_pipeline


def test_end_to_end_pipeline_and_no_leakage(tmp_path: Path):
    raw = tmp_path / "data/raw"
    for label_index, label in enumerate(("real", "fake")):
        (raw / label).mkdir(parents=True)
        for index in range(10):
            sr = 8000 if index % 2 else 16000
            time = np.arange(sr * 6, dtype=np.float32) / sr
            audio = (.08 + index * .001) * np.sin(2 * np.pi * (220 + label_index * 110 + index) * time)
            sf.write(raw / label / f"{index}.wav", audio, sr)
    config = {
        "dataset": {"raw_dir": "data/raw", "processed_dir": "data/processed",
                    "metadata_dir": "data/metadata", "reports_dir": "reports"},
        "audio": {"sample_rate": 16000, "channels": 1, "normalize": True},
        "validation": {"minimum_duration_seconds": .1, "supported_sample_rates": [8000, 16000],
                       "silence_threshold": .0001, "silent_fraction_warning": .99},
        "segmentation": {"duration_seconds": 5., "hop_seconds": 2.5, "short_audio_policy": "pad"},
        "split": {"train": .7, "validation": .15, "test": .15, "random_seed": 42},
        "augmentation": {"enabled": False},
    }
    config_dir = tmp_path / "configs"; config_dir.mkdir()
    config_path = config_dir / "preprocessing.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    summary = run_pipeline(config_path)
    metadata = pd.read_csv(tmp_path / "data/metadata/processed_metadata.csv")
    assert summary["processing_failures"] == 0 and len(metadata) == 20
    assert set(metadata["sample_rate"]) == {16000} and set(metadata["channels"]) == {1}
    assert metadata.groupby("source_file")["split"].nunique().max() == 1
    assert metadata.groupby("source_file_hash")["split"].nunique().max() == 1
    assert all(Path(path).exists() for path in metadata["file_path"])
