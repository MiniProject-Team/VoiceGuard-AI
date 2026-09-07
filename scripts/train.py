from __future__ import annotations
import argparse, json, logging, sys
from pathlib import Path
import pandas as pd
import torch, yaml
from torch.utils.data import DataLoader
from transformers import AutoProcessor
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.models.dataset import AudioClassificationDataset, Wav2VecDataCollator
from src.models.trainer import ModelTrainer
from src.models.utils import class_weights, load_yaml, resolve_path, set_seed, verify_split_leakage
from src.models.wav2vec_model import Wav2VecDeepfakeClassifier
from src.models.readiness import assess_training_frames, reject_debug_or_random_artifact

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", default=str(ROOT / "configs/training.yaml")); args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cp = Path(args.config).resolve(); cfg = load_yaml(cp); base = cp.parent.parent; tc, ac, paths = cfg["training"], cfg["audio"], cfg["paths"]
    set_seed(int(tc["seed"])); device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    frames = {name: pd.read_csv(resolve_path(paths[f"{name}_csv"], base)) for name in ("train", "validation", "test")}
    verify_split_leakage(frames)
    reject_debug_or_random_artifact(cfg)
    readiness = assess_training_frames(frames)
    if not readiness.ready:
        raise RuntimeError("DATASET_INSUFFICIENT: " + "; ".join(readiness.reasons))
    limits = {name: None for name in frames}
    model_name = cfg["model"]["name"]
    logging.info("Device=%s model=%s sizes=%s batch=%s lr=%s epochs=%s", device, model_name, {k: len(v) for k,v in frames.items()}, tc["batch_size"], tc["learning_rate"], tc["epochs"])
    processor = AutoProcessor.from_pretrained(model_name)
    datasets = {name: AudioClassificationDataset(frame, int(ac["sample_rate"]), float(ac["max_duration_seconds"]), limits[name]) for name, frame in frames.items()}
    collator = Wav2VecDataCollator(processor, int(ac["sample_rate"])); loaders = {name: DataLoader(ds, batch_size=int(tc["batch_size"]), shuffle=name=="train", num_workers=int(tc["num_workers"]), pin_memory=device.type=="cuda", collate_fn=collator) for name, ds in datasets.items()}
    model = Wav2VecDeepfakeClassifier(model_name, int(cfg["model"]["num_labels"]), float(cfg["model"]["dropout"])); model.configure_trainable_layers(bool(tc["freeze_feature_extractor"]), int(tc["unfreeze_encoder_layers"]))
    weights = class_weights(frames["train"]["label"]) if tc.get("use_class_weights") else None
    trainer = ModelTrainer(model, processor, loaders["train"], loaders["validation"], cfg, device, weights)
    checkpoint, best, reports = (resolve_path(paths[key], base) for key in ("checkpoint_dir", "best_model_dir", "report_dir"))
    history = trainer.train(checkpoint, best, reports)
    validation = pd.read_csv(reports / "best_validation_predictions.csv")
    candidates = __import__("src.models.metrics", fromlist=["threshold_analysis"]).threshold_analysis(validation.true_label, validation.probability_fake, float(cfg["evaluation"]["threshold_start"]), float(cfg["evaluation"]["threshold_stop"]), float(cfg["evaluation"]["threshold_step"]))
    selected = candidates.sort_values(["f1", "false_negative_rate", "threshold"], ascending=[False, True, True]).iloc[0]
    threshold = float(selected["threshold"])
    candidates.to_csv(reports / "threshold_analysis.csv", index=False)
    model_info = {"base_model": model_name, "configured_base_model": cfg["model"]["name"], "sample_rate": ac["sample_rate"], "max_duration_seconds": ac["max_duration_seconds"], "label_mapping": {"0":"REAL", "1":"SYNTHETIC"}, "threshold": threshold, "threshold_selection": {"split":"validation", "criterion":"max_f1_then_min_fnr"}, "training_epochs_completed": len(history), "learning_rate": tc["learning_rate"], "seed": tc["seed"], "debug_mode": False, "validation_metrics": history[-1] if history else {}}
    (best / "model_config.json").write_text(json.dumps(model_info, indent=2), encoding="utf-8"); (best / "training_config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

if __name__ == "__main__": main()
