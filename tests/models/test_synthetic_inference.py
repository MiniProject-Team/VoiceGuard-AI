import json
from pathlib import Path

import numpy as np
import torch

from api.routes.analysis import response_for
from mlops.model_registry import ModelRegistry
from src.models.synthetic_preprocessing import prepare_synthetic_waveform
from src.models.utils import load_yaml
from src.realtime.adapters import SyntheticDetectorAdapter
from src.risk import RiskEngine

ROOT = Path(__file__).resolve().parents[2]


def test_registered_synthetic_checkpoint_and_mapping_are_valid():
    model_dir = ROOT / "models/best_model"
    info = json.loads((model_dir / "model_config.json").read_text())
    registry = ModelRegistry(ROOT / "models/registry/synthetic_detector/registry.json")
    active = [item for item in registry.data["models"] if item["status"] == "ACTIVE"]
    assert (model_dir / "model.pt").is_file()
    assert active and Path(active[0]["artifact_path"]).resolve() == model_dir.resolve()
    assert registry.validate_hash(active[0]["model_id"])
    assert info["label_mapping"] == {"0": "REAL", "1": "FAKE"}


def test_synthetic_preprocessing_is_deterministic_and_preserves_input_differences():
    first = np.linspace(-0.25, 0.25, 8000, dtype=np.float32)
    second = np.sin(np.linspace(0, 100, 8000, dtype=np.float32)).astype(np.float32)
    prepared_first = prepare_synthetic_waveform(first, 16000, 16000, 5.0)
    assert np.array_equal(prepared_first, prepare_synthetic_waveform(first, 16000, 16000, 5.0))
    assert prepared_first.shape == (80000,)
    assert prepared_first.dtype == np.float32
    assert not np.array_equal(prepared_first, prepare_synthetic_waveform(second, 16000, 16000, 5.0))


def test_adapter_probability_is_bounded_deterministic_and_uses_configured_synthetic_class():
    class Processor:
        def __call__(self, waveform, **_): return {"input_values": torch.tensor(waveform).unsqueeze(0)}
    class Model:
        def __call__(self, **_): return {"logits": torch.tensor([[0.0, 1.0]])}
    adapter = SyntheticDetectorAdapter.__new__(SyntheticDetectorAdapter)
    adapter.sample_rate, adapter.max_duration_seconds, adapter.threshold = 16000, 0.01, 0.5
    adapter.synthetic_class, adapter.real_class, adapter.device = 0, 1, torch.device("cpu")
    adapter.processor, adapter.model = Processor(), Model()
    waveform = np.ones(160, dtype=np.float32) * 0.1
    first, second = adapter.diagnose(waveform), adapter.diagnose(waveform)
    assert 0 <= first["synthetic_probability"] <= 1
    assert first["synthetic_probability"] == second["synthetic_probability"]
    assert first["synthetic_probability"] < first["real_probability"]


def test_api_response_preserves_model_probability_and_risk_consumes_it():
    synthetic_probability = 0.42
    risk = RiskEngine(load_yaml(ROOT / "configs/risk_engine.yaml")).evaluate({"synthetic_probability": synthetic_probability})
    raw = {"segment_id": 1, "synthetic_probability": synthetic_probability, "speaker_similarity": None, "risk_score": risk["risk_score"], "risk_level": risk["risk_level"], "decision": risk["decision"], "recommended_action": risk["recommended_action"], "alert_event": None}
    response = response_for("SESSION_TEST", raw)
    assert response.analysis.synthetic_probability == synthetic_probability
    assert risk["signal_breakdown"]["synthetic_voice"] == 18.9
