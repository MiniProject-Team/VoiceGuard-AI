"""On-demand audio dataset and Wav2Vec2 batch collation."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from src.data.audio_utils import convert_to_mono, load_audio, resample_audio

class AudioClassificationDataset(Dataset):
    def __init__(self, metadata: str | Path | pd.DataFrame, sample_rate: int = 16000,
                 max_duration_seconds: float = 5.0, max_samples: int | None = None):
        self.frame = pd.read_csv(metadata) if not isinstance(metadata, pd.DataFrame) else metadata.copy()
        if not {"file_path", "label"}.issubset(self.frame): raise ValueError("Metadata requires file_path and label")
        self.frame = self.frame.iloc[:max_samples].reset_index(drop=True) if max_samples else self.frame.reset_index(drop=True)
        self.sample_rate, self.max_samples = sample_rate, round(sample_rate * max_duration_seconds)
    def __len__(self) -> int: return len(self.frame)
    def __getitem__(self, index: int) -> dict[str, Any]:
        row = self.frame.iloc[index]; path = Path(str(row["file_path"]))
        if not path.exists(): raise FileNotFoundError(f"Audio not found: {path}")
        audio, sr = load_audio(path); audio = convert_to_mono(audio)
        audio = resample_audio(audio, sr, self.sample_rate)[:self.max_samples].astype(np.float32)
        return {"input_values": audio, "labels": int(row["label"]), "metadata": row.to_dict()}

class Wav2VecDataCollator:
    def __init__(self, processor: Any, sample_rate: int = 16000): self.processor, self.sample_rate = processor, sample_rate
    def __call__(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        batch = self.processor([item["input_values"] for item in features], sampling_rate=self.sample_rate,
                               padding=True, return_tensors="pt")
        batch["labels"] = torch.tensor([item["labels"] for item in features], dtype=torch.long)
        batch["metadata"] = [item["metadata"] for item in features]
        return batch
