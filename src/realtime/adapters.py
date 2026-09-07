"""Preloaded adapters for the Phase 3 synthetic detector and Phase 4 verifier."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import torch
from transformers import AutoProcessor

from src.models.synthetic_preprocessing import prepare_synthetic_waveform, waveform_statistics
from src.models.wav2vec_model import Wav2VecDeepfakeClassifier
from src.models.readiness import reject_debug_or_random_artifact
from src.models.utils import load_yaml, resolve_path
from src.speaker.embedding import extract_embedding_from_waveform, load_speaker_model
from src.speaker.enrollment import load_enrollment
from src.speaker.similarity import cosine_similarity

LOGGER = logging.getLogger(__name__)


class SyntheticDetectorAdapter:
    """Load the registered Phase 3 checkpoint and emit P(audio is synthetic)."""

    def __init__(self, model_dir: Path):
        self.model_dir = Path(model_dir)
        checkpoint = self.model_dir / "model.pt"
        config_path = self.model_dir / "model_config.json"
        training_path = self.model_dir / "training_config.yaml"
        if not checkpoint.is_file():
            raise FileNotFoundError(f"Synthetic detector checkpoint is missing: {checkpoint}")
        if not config_path.is_file() or not training_path.is_file():
            raise FileNotFoundError("Synthetic detector metadata is incomplete.")

        info = json.loads(config_path.read_text(encoding="utf-8"))
        training = load_yaml(training_path)
        reject_debug_or_random_artifact(training, info)
        trained_model_name = training["model"]["name"]
        if info.get("base_model") != trained_model_name:
            raise ValueError("Model metadata base_model does not match the training architecture.")
        self.sample_rate = int(info["sample_rate"])
        self.max_duration_seconds = float(info["max_duration_seconds"])
        self.threshold = float(info["threshold"])
        mapping = {int(key): str(value).upper() for key, value in info["label_mapping"].items()}
        synthetic = [index for index, label in mapping.items() if label in {"FAKE", "SYNTHETIC"}]
        real = [index for index, label in mapping.items() if label == "REAL"]
        num_labels = int(training["model"]["num_labels"])
        if len(mapping) != num_labels or mapping.get(0) != "REAL" or len(synthetic) != 1 or len(real) != 1:
            raise ValueError("Model label mapping must contain exactly one REAL and one FAKE/SYNTHETIC class.")
        self.synthetic_class, self.real_class = synthetic[0], real[0]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoProcessor.from_pretrained(self.model_dir)
        # from_directory uses strict state-dict loading.  Any checkpoint/architecture
        # mismatch propagates and prevents the API from advertising a ready model.
        self.model = Wav2VecDeepfakeClassifier.from_directory(
            self.model_dir,
            info["base_model"],
            num_labels=num_labels,
            dropout=float(training["model"]["dropout"]),
        ).to(self.device).eval()
        LOGGER.info(
            "Loaded Phase 3 checkpoint=%s base_model=%s labels=%s synthetic_class=%d",
            checkpoint, info["base_model"], mapping, self.synthetic_class,
        )

    def prepare(self, waveform: np.ndarray, source_sample_rate: int | None = None) -> np.ndarray:
        return prepare_synthetic_waveform(
            waveform,
            self.sample_rate if source_sample_rate is None else source_sample_rate,
            self.sample_rate,
            self.max_duration_seconds,
            pad_to_duration=True,
        )

    @torch.no_grad()
    def diagnose(self, waveform: np.ndarray, source_sample_rate: int | None = None) -> dict:
        prepared = self.prepare(waveform, source_sample_rate)
        batch = self.processor(prepared, sampling_rate=self.sample_rate, return_tensors="pt", padding=True)
        batch = {key: value.to(self.device) for key, value in batch.items()}
        logits = self.model(**batch)["logits"][0]
        probabilities = torch.softmax(logits, dim=-1)
        synthetic_probability = float(probabilities[self.synthetic_class].item())
        real_probability = float(probabilities[self.real_class].item())
        predicted_class = int(torch.argmax(probabilities).item())
        return {
            "input": waveform_statistics(prepared, self.sample_rate),
            "input_tensor_shape": list(batch["input_values"].shape),
            "dtype": str(batch["input_values"].dtype),
            "device": str(self.device),
            "raw_logits": [float(value) for value in logits.detach().cpu().tolist()],
            "probabilities": [float(value) for value in probabilities.detach().cpu().tolist()],
            "real_probability": real_probability,
            "synthetic_probability": synthetic_probability,
            "predicted_class": predicted_class,
            "classification": "FAKE" if synthetic_probability >= self.threshold else "REAL",
            "threshold": self.threshold,
        }

    @torch.no_grad()
    def __call__(self, waveform: np.ndarray) -> dict:
        diagnostic = self.diagnose(waveform)
        LOGGER.debug(
            "phase3_preprocess sample_rate=%s duration=%s min=%s max=%s mean=%s std=%s input_shape=%s dtype=%s device=%s logits=%s probabilities=%s predicted_class=%s synthetic_probability=%s",
            diagnostic["input"]["sample_rate"], diagnostic["input"]["duration_seconds"], diagnostic["input"]["minimum"], diagnostic["input"]["maximum"], diagnostic["input"]["mean"], diagnostic["input"]["std"], diagnostic["input_tensor_shape"], diagnostic["dtype"], diagnostic["device"], diagnostic["raw_logits"], diagnostic["probabilities"], diagnostic["predicted_class"], diagnostic["synthetic_probability"],
        )
        return {"synthetic_probability": diagnostic["synthetic_probability"], "classification": diagnostic["classification"]}


class SpeakerVerifierAdapter:
    def __init__(self, config_path: Path, root: Path):
        cfg = load_yaml(config_path); self.cfg = cfg
        self.model = load_speaker_model(cfg["model"]["name"], savedir=root / "models/speaker_verification/model_cache")
        cal = resolve_path(cfg["paths"]["calibrated_threshold"], root)
        self.threshold = cfg["verification"]["threshold"]
        if cal.exists():
            calibration = json.loads(cal.read_text())
            minimum = int(cfg["verification"].get("minimum_calibration_trials_per_class", 20))
            genuine = int(calibration.get("genuine_validation_trials", 0))
            impostor = int(calibration.get("impostor_validation_trials", 0))
            if not calibration.get("demo", True) and genuine >= minimum and impostor >= minimum:
                self.threshold = float(calibration["threshold"])
            else:
                LOGGER.warning("Speaker threshold is not usable: calibration needs %d genuine and impostor non-demo validation trials.", minimum)
        self.embedding_dir = resolve_path(cfg["paths"]["embedding_dir"], root)

    def __call__(self, speaker_id: str, waveform: np.ndarray) -> dict:
        try: template, _ = load_enrollment(speaker_id, self.embedding_dir)
        except KeyError: return {"similarity": None, "verified": None, "status": "speaker_not_enrolled"}
        embedding = extract_embedding_from_waveform(waveform, int(self.cfg["audio"]["sample_rate"]), self.model, int(self.cfg["audio"]["sample_rate"]), True)
        similarity = cosine_similarity(template, embedding)
        if self.threshold is None: return {"similarity": similarity, "verified": None, "status": "threshold_not_calibrated"}
        return {"similarity": similarity, "verified": similarity >= self.threshold, "status": "ok"}


class MockSyntheticDetector:
    def __init__(self, probability=.1): self.probability = probability
    def __call__(self, waveform): return {"synthetic_probability": self.probability, "classification": "FAKE" if self.probability >= .5 else "REAL"}


class MockSpeakerVerifier:
    def __init__(self, similarity=.9): self.similarity = similarity
    def __call__(self, speaker_id, waveform): return {"similarity": self.similarity, "verified": self.similarity >= .7, "status": "ok"}
