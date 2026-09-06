"""Batch and single-file model inference."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np
import torch
from torch.utils.data import DataLoader
from .dataset import AudioClassificationDataset, Wav2VecDataCollator

@torch.no_grad()
def predict_loader(model: torch.nn.Module, loader: DataLoader, device: torch.device) -> list[dict[str, Any]]:
    model.eval(); rows = []
    for batch in loader:
        metadata = batch.pop("metadata"); labels = batch.pop("labels"); batch = {key: value.to(device) for key, value in batch.items()}
        probabilities = torch.softmax(model(**batch)["logits"], dim=-1).cpu().numpy()
        for meta, label, probability in zip(metadata, labels.tolist(), probabilities):
            rows.append({"audio_path": meta["file_path"], "true_label": label,
                         "probability_real": float(probability[0]), "probability_fake": float(probability[1]),
                         "speaker_id": meta.get("speaker_id"), "language": meta.get("language"),
                         "source_dataset": meta.get("source_dataset")})
    return rows

def predict_file(model: torch.nn.Module, processor: Any, audio_path: str | Path, device: torch.device,
                 sample_rate=16000, max_duration_seconds=5., threshold=.5) -> dict[str, Any]:
    import pandas as pd
    dataset = AudioClassificationDataset(pd.DataFrame([{"file_path": str(audio_path), "label": 0}]), sample_rate, max_duration_seconds)
    loader = DataLoader(dataset, batch_size=1, collate_fn=Wav2VecDataCollator(processor, sample_rate))
    row = predict_loader(model, loader, device)[0]; row["predicted_label"] = int(row["probability_fake"] >= threshold); row["threshold"] = threshold
    return row
