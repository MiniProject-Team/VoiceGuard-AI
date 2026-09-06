"""CPU/GPU training loop with validation, checkpoints, and early stopping."""
from __future__ import annotations
import json, logging, shutil
from pathlib import Path
from typing import Any
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import torch
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup
from .inference import predict_loader
from .metrics import compute_metrics, save_evaluation_reports, threshold_analysis

LOGGER = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, model: nn.Module, processor: Any, train_loader: DataLoader, validation_loader: DataLoader,
                 config: dict[str, Any], device: torch.device, weights: torch.Tensor | None = None):
        self.model, self.processor, self.train_loader, self.validation_loader = model.to(device), processor, train_loader, validation_loader
        self.config, self.device = config, device
        self.loss_fn = nn.CrossEntropyLoss(weight=weights.to(device) if weights is not None else None)
        train_cfg = config["training"]
        self.optimizer = AdamW((p for p in model.parameters() if p.requires_grad), lr=float(train_cfg["learning_rate"]), weight_decay=float(train_cfg["weight_decay"]))
        updates = max(1, len(train_loader) * int(train_cfg["epochs"]) // int(train_cfg["gradient_accumulation_steps"]))
        self.scheduler = get_linear_schedule_with_warmup(self.optimizer, int(updates * float(train_cfg["warmup_ratio"])), updates)
        self.use_amp = bool(train_cfg.get("mixed_precision", True) and device.type == "cuda")
        self.scaler = torch.amp.GradScaler("cuda", enabled=self.use_amp)
    def _train_epoch(self, threshold: float) -> tuple[float, dict[str, Any]]:
        self.model.train(); total, accumulation, labels_all, probabilities = 0., int(self.config["training"]["gradient_accumulation_steps"]), [], []
        self.optimizer.zero_grad(set_to_none=True)
        for index, batch in enumerate(self.train_loader, 1):
            batch.pop("metadata"); labels = batch.pop("labels").to(self.device); values = {k: v.to(self.device) for k, v in batch.items()}
            with torch.amp.autocast("cuda", enabled=self.use_amp):
                logits = self.model(**values)["logits"]; loss = self.loss_fn(logits, labels) / accumulation
            labels_all.extend(labels.detach().cpu().tolist()); probabilities.extend(torch.softmax(logits.detach(), -1)[:, 1].cpu().tolist())
            self.scaler.scale(loss).backward(); total += float(loss.item()) * accumulation
            if index % accumulation == 0 or index == len(self.train_loader):
                self.scaler.step(self.optimizer); self.scaler.update(); self.optimizer.zero_grad(set_to_none=True); self.scheduler.step()
        return total / max(1, len(self.train_loader)), compute_metrics(labels_all, probabilities, threshold)
    def _validation(self, threshold: float) -> tuple[float, dict[str, Any], pd.DataFrame]:
        self.model.eval(); losses, rows = [], []
        with torch.no_grad():
            for batch in self.validation_loader:
                metadata = batch.pop("metadata"); labels = batch.pop("labels").to(self.device); values = {k: v.to(self.device) for k, v in batch.items()}
                logits = self.model(**values)["logits"]; losses.append(float(self.loss_fn(logits, labels).item()))
                probs = torch.softmax(logits, -1).cpu().numpy()
                for meta, label, prob in zip(metadata, labels.cpu().tolist(), probs): rows.append({"audio_path": meta["file_path"], "true_label": label, "probability_real": float(prob[0]), "probability_fake": float(prob[1])})
        frame = pd.DataFrame(rows); return sum(losses) / max(1, len(losses)), compute_metrics(frame.true_label, frame.probability_fake, threshold), frame
    def train(self, checkpoint_dir: Path, best_dir: Path, report_dir: Path) -> list[dict[str, Any]]:
        cfg, eval_cfg = self.config["training"], self.config["evaluation"]
        checkpoint_dir.mkdir(parents=True, exist_ok=True); best_dir.mkdir(parents=True, exist_ok=True); report_dir.mkdir(parents=True, exist_ok=True)
        history, best, stale = [], float("-inf"), 0
        for epoch in range(1, int(cfg["epochs"]) + 1):
            train_loss, train_metrics = self._train_epoch(float(eval_cfg["threshold"])); val_loss, metrics, predictions = self._validation(float(eval_cfg["threshold"]))
            row = {"epoch": epoch, "train_loss": train_loss, "validation_loss": val_loss,
                   **{f"train_{key}": value for key, value in train_metrics.items() if key != "confusion_matrix"}, **metrics}; history.append(row)
            LOGGER.info("Epoch %d/%d Train Loss %.4f Val Loss %.4f Val F1 %.4f Val AUC %s", epoch, cfg["epochs"], train_loss, val_loss, metrics["f1"], metrics["roc_auc"])
            epoch_dir = checkpoint_dir / f"epoch-{epoch}"; self.model.save_pretrained(epoch_dir)
            score = metrics.get(cfg.get("selection_metric", "f1")); score = float(score) if score is not None else float("-inf")
            if score > best:
                best, stale = score, 0; self.model.save_pretrained(best_dir); self.processor.save_pretrained(best_dir)
                predictions.to_csv(report_dir / "best_validation_predictions.csv", index=False)
            else: stale += 1
            if stale >= int(cfg.get("early_stopping_patience", 2)): break
        history_frame = pd.DataFrame(history); history_frame.to_csv(report_dir / "training_history.csv", index=False)
        for column, filename in (("train_loss", "training_loss.png"), ("validation_loss", "validation_loss.png"), ("f1", "f1_curve.png"), ("roc_auc", "auc_curve.png")):
            plt.figure(); plt.plot(history_frame.epoch, history_frame[column], marker="o"); plt.xlabel("Epoch"); plt.ylabel(column); plt.tight_layout(); plt.savefig(report_dir / filename); plt.close()
        if not predictions.empty:
            threshold_analysis(predictions.true_label.to_numpy(), predictions.probability_fake.to_numpy(), float(eval_cfg["threshold_start"]), float(eval_cfg["threshold_stop"]), float(eval_cfg["threshold_step"])).to_csv(report_dir / "threshold_analysis.csv", index=False)
            save_evaluation_reports(predictions, report_dir, float(eval_cfg["threshold"]), "validation")
        return history
