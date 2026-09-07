from __future__ import annotations
import argparse, json, logging, sys
from pathlib import Path
import pandas as pd, torch
from torch.utils.data import DataLoader
from transformers import AutoProcessor
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.models.dataset import AudioClassificationDataset, Wav2VecDataCollator
from src.models.inference import predict_loader
from src.models.metrics import save_evaluation_reports
from src.models.utils import load_yaml, resolve_path
from src.models.wav2vec_model import Wav2VecDeepfakeClassifier
from src.models.readiness import reject_debug_or_random_artifact

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--model", required=True); parser.add_argument("--config", default=str(ROOT / "configs/training.yaml")); args = parser.parse_args()
    logging.basicConfig(level=logging.INFO); cp = Path(args.config).resolve(); cfg = load_yaml(cp); base = cp.parent.parent; model_dir = resolve_path(args.model, base)
    info = json.loads((model_dir / "model_config.json").read_text()); reject_debug_or_random_artifact(cfg, info); model_name = info["base_model"]; device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = AutoProcessor.from_pretrained(model_dir); model = Wav2VecDeepfakeClassifier.from_directory(model_dir, model_name, num_labels=int(cfg["model"]["num_labels"]), dropout=float(cfg["model"]["dropout"])).to(device)
    csv = resolve_path(cfg["paths"]["test_csv"], base); maximum = None
    dataset = AudioClassificationDataset(csv, int(cfg["audio"]["sample_rate"]), float(cfg["audio"]["max_duration_seconds"]), maximum)
    loader = DataLoader(dataset, batch_size=int(cfg["training"]["batch_size"]), collate_fn=Wav2VecDataCollator(processor, int(cfg["audio"]["sample_rate"])))
    predictions = pd.DataFrame(predict_loader(model, loader, device)); report = resolve_path(cfg["paths"]["report_dir"], base); metrics = save_evaluation_reports(predictions, report, float(info["threshold"]), "test")
    info["test_metrics"] = metrics; (model_dir / "model_config.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    history_path = report / "training_history.csv"; comparison = {"test": metrics}
    if history_path.exists():
        history = pd.read_csv(history_path); last = history.iloc[-1]
        comparison["training"] = {key.removeprefix("train_"): value for key, value in last.items() if key.startswith("train_")}
        comparison["validation"] = {key: last[key] for key in ("accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc") if key in last}
        train_f1, test_f1 = comparison["training"].get("f1"), metrics.get("f1")
        comparison["generalization_warning"] = bool(train_f1 is not None and test_f1 is not None and float(train_f1) - float(test_f1) > .15)
    (report / "generalization_comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8"); print(json.dumps(metrics, indent=2))

if __name__ == "__main__": main()
