import numpy as np, pandas as pd, pytest, soundfile as sf
from src.models.dataset import AudioClassificationDataset

def test_metadata_audio_and_label(tmp_path):
    path = tmp_path / "audio.wav"; sf.write(path, np.zeros((800, 2), dtype=np.float32), 8000)
    dataset = AudioClassificationDataset(pd.DataFrame([{"file_path": str(path), "label": "1"}]), 16000, .2)
    item = dataset[0]; assert item["labels"] == 1 and item["input_values"].dtype == np.float32 and item["input_values"].ndim == 1

def test_missing_file():
    dataset = AudioClassificationDataset(pd.DataFrame([{"file_path": "missing.wav", "label": 0}]))
    with pytest.raises(FileNotFoundError): dataset[0]
