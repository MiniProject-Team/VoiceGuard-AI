from types import SimpleNamespace
import torch
from torch import nn
from src.models.wav2vec_model import Wav2VecDeepfakeClassifier

class TinyBackbone(nn.Module):
    def __init__(self): super().__init__(); self.config = SimpleNamespace(hidden_size=8); self.projection = nn.Linear(1, 8)
    def forward(self, input_values, attention_mask=None): return SimpleNamespace(last_hidden_state=self.projection(input_values[:, ::4].unsqueeze(-1)))

def test_model_initializes_and_forward_shape():
    model = Wav2VecDeepfakeClassifier("mock", backbone=TinyBackbone())
    output = model(torch.zeros(3, 100))["logits"]
    assert output.shape == (3, 2)
