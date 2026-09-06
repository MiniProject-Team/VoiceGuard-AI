"""Security-oriented classification metrics, plots, and subgroup analysis."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
    confusion_matrix, f1_score, precision_recall_curve, precision_score, recall_score,
    roc_auc_score, roc_curve)

def compute_metrics(y_true: np.ndarray, probability_fake: np.ndarray, threshold: float = .5) -> dict[str, Any]:
    y, p = np.asarray(y_true, dtype=int), np.asarray(probability_fake, dtype=float)
    pred = (p >= threshold).astype(int); tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    safe = lambda a, b: float(a / b) if b else 0.0
    return {"accuracy": float(accuracy_score(y, pred)), "precision": float(precision_score(y, pred, zero_division=0)),
            "recall": float(recall_score(y, pred, zero_division=0)), "f1": float(f1_score(y, pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
            "pr_auc": float(average_precision_score(y, p)) if len(np.unique(y)) == 2 else None,
            "specificity": safe(tn, tn + fp), "false_positive_rate": safe(fp, fp + tn),
            "false_negative_rate": safe(fn, fn + tp),
            "false_acceptance_rate": safe(fn, fn + tp), "false_rejection_rate": safe(fp, fp + tn),
            "brier_score": float(brier_score_loss(y, p)), "threshold": threshold,
            "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]]}

def threshold_analysis(y_true: np.ndarray, probabilities: np.ndarray, start=.1, stop=.9, step=.05) -> pd.DataFrame:
    return pd.DataFrame([compute_metrics(y_true, probabilities, float(t)) for t in np.arange(start, stop + step / 2, step)])

def subgroup_metrics(frame: pd.DataFrame, group: str) -> pd.DataFrame:
    rows = []
    if group not in frame: return pd.DataFrame()
    for value, subset in frame.dropna(subset=[group]).groupby(group):
        row = compute_metrics(subset["true_label"].to_numpy(), subset["probability_fake"].to_numpy(),
                              float(subset["threshold"].iloc[0])); row[group] = value; row["sample_count"] = len(subset); rows.append(row)
    return pd.DataFrame(rows)

def save_evaluation_reports(predictions: pd.DataFrame, report_dir: str | Path, threshold: float,
                            prefix: str = "test") -> dict[str, Any]:
    os.environ.setdefault("MPLBACKEND", "Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    out = Path(report_dir); out.mkdir(parents=True, exist_ok=True)
    y, p = predictions["true_label"].to_numpy(), predictions["probability_fake"].to_numpy()
    predictions = predictions.copy(); predictions["predicted_label"] = (p >= threshold).astype(int); predictions["threshold"] = threshold
    metrics = compute_metrics(y, p, threshold)
    (out / f"{prefix}_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    predictions.to_csv(out / f"{prefix}_predictions.csv", index=False)
    predictions[(predictions.true_label == 0) & (predictions.predicted_label == 1)].to_csv(out / "false_positives.csv", index=False)
    predictions[(predictions.true_label == 1) & (predictions.predicted_label == 0)].to_csv(out / "false_negatives.csv", index=False)
    cm = np.asarray(metrics["confusion_matrix"]); plt.figure(); sns.heatmap(cm, annot=True, fmt="d", xticklabels=["Real", "Fake"], yticklabels=["Real", "Fake"]); plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.tight_layout(); plt.savefig(out / "confusion_matrix.png"); plt.close()
    if len(np.unique(y)) == 2:
        fpr, tpr, _ = roc_curve(y, p); plt.figure(); plt.plot(fpr, tpr); plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate"); plt.tight_layout(); plt.savefig(out / "roc_curve.png"); plt.close()
        precision, recall, _ = precision_recall_curve(y, p); plt.figure(); plt.plot(recall, precision); plt.xlabel("Recall"); plt.ylabel("Precision"); plt.tight_layout(); plt.savefig(out / "pr_curve.png"); plt.close()
        fraction, mean = calibration_curve(y, p, n_bins=min(10, len(y)), strategy="uniform"); plt.figure(); plt.plot(mean, fraction, marker="o"); plt.plot([0,1],[0,1], "--"); plt.xlabel("Mean predicted probability"); plt.ylabel("Observed fake fraction"); plt.tight_layout(); plt.savefig(out / "calibration_curve.png"); plt.close()
    for group in ("language", "source_dataset"):
        result = subgroup_metrics(predictions, group)
        if not result.empty: result.to_csv(out / f"metrics_by_{group}.csv", index=False)
    return metrics
