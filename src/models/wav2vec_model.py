"""Wav2Vec2 mean-pooled binary classifier."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import torch
from torch import nn
from transformers import Wav2Vec2Model

class Wav2VecDeepfakeClassifier(nn.Module):
    def __init__(self, model_name: str, num_labels: int = 2, dropout: float = .2,
                 backbone: nn.Module | None = None):
        super().__init__(); self.model_name = model_name
        self.wav2vec2 = backbone if backbone is not None else Wav2Vec2Model.from_pretrained(model_name)
        hidden = int(self.wav2vec2.config.hidden_size)
        self.dropout, self.classifier = nn.Dropout(dropout), nn.Linear(hidden, num_labels)
    def forward(self, input_values: torch.Tensor, attention_mask: torch.Tensor | None = None) -> dict[str, torch.Tensor]:
        output = self.wav2vec2(input_values=input_values, attention_mask=attention_mask)
        hidden = output.last_hidden_state
        if attention_mask is None:
            pooled = hidden.mean(dim=1)
        else:
            feature_mask = self.wav2vec2._get_feature_vector_attention_mask(hidden.shape[1], attention_mask)
            weights = feature_mask.unsqueeze(-1).to(hidden.dtype)
            pooled = (hidden * weights).sum(1) / weights.sum(1).clamp_min(1)
        return {"logits": self.classifier(self.dropout(pooled))}
    def configure_trainable_layers(self, freeze_feature_extractor: bool = True, unfreeze_encoder_layers: int = 0) -> None:
        for parameter in self.wav2vec2.parameters(): parameter.requires_grad = not freeze_feature_extractor
        if freeze_feature_extractor and unfreeze_encoder_layers > 0 and hasattr(self.wav2vec2, "encoder"):
            for layer in self.wav2vec2.encoder.layers[-unfreeze_encoder_layers:]:
                for parameter in layer.parameters(): parameter.requires_grad = True
    def save_pretrained(self, directory: str | Path) -> None:
        directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), directory / "model.pt")
    @classmethod
    def from_directory(cls, directory: str | Path, model_name: str, **kwargs: Any) -> "Wav2VecDeepfakeClassifier":
        checkpoint = Path(directory) / "model.pt"
        if not checkpoint.is_file():
            raise FileNotFoundError(f"Model checkpoint is missing: {checkpoint}")
        model = cls(model_name, **kwargs)
        try:
            state = torch.load(checkpoint, map_location="cpu", weights_only=True)
            model.load_state_dict(state, strict=True)
        except Exception as exc:
            raise RuntimeError(f"Checkpoint could not be strictly loaded: {checkpoint}") from exc
        return model
