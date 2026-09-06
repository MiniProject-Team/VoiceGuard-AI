from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import torch
from transformers import AutoProcessor
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.models.inference import predict_file
from src.models.wav2vec_model import Wav2VecDeepfakeClassifier

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--model", required=True); parser.add_argument("--audio", required=True); args = parser.parse_args()
    model_dir = Path(args.model); info = json.loads((model_dir / "model_config.json").read_text()); device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = AutoProcessor.from_pretrained(model_dir); model = Wav2VecDeepfakeClassifier.from_directory(model_dir, info["base_model"]).to(device)
    result = predict_file(model, processor, args.audio, device, int(info["sample_rate"]), float(info["max_duration_seconds"]), float(info["threshold"]))
    print(f"Audio: {args.audio}\n\nPrediction: {'FAKE' if result['predicted_label'] else 'REAL'}\n\nProbability Real: {result['probability_real']:.4f}\nProbability Fake: {result['probability_fake']:.4f}\n\nThreshold: {result['threshold']:.2f}")
    print("Probabilities are model estimates and may require calibration.")

if __name__ == "__main__": main()
