"""Speaker trial construction, evaluation metrics, and biometric plots."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Callable
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve
from .similarity import cosine_similarity
from .threshold import analyze_thresholds, calculate_eer, metrics_at_threshold

def create_trials(metadata: pd.DataFrame, embeddings: dict[str, np.ndarray], enrollment_files: set[str] | None = None) -> pd.DataFrame:
    if "speaker_id" not in metadata or metadata.speaker_id.isna().any(): raise ValueError("Speaker verification evaluation requires speaker_id metadata")
    excluded = {str(Path(path).resolve()) for path in (enrollment_files or set())}; rows = []
    speakers = sorted(metadata.speaker_id.unique())
    for index, record in metadata.iterrows():
        path = str(Path(record.file_path).resolve())
        if path in excluded: raise ValueError(f"Enrollment/test leakage: {path}")
        for reference in speakers:
            trial_type = "genuine" if reference == record.speaker_id else "impostor"
            rows.append({"trial_id": f"{index}_{reference}", "reference_speaker": reference, "test_speaker": record.speaker_id,
                         "trial_type": trial_type, "similarity": cosine_similarity(embeddings[reference], embeddings[path]),
                         "audio_path": path, "language": record.get("language"), "source_dataset": record.get("source_dataset"),
                         "attack_type": record.get("attack_type")})
    return pd.DataFrame(rows)

def evaluate_trials(trials: pd.DataFrame, threshold: float, report_dir: str | Path) -> dict[str, float]:
    os.environ.setdefault("MPLBACKEND", "Agg"); import matplotlib.pyplot as plt
    out = Path(report_dir); out.mkdir(parents=True, exist_ok=True); labels = (trials.trial_type == "genuine").astype(int).to_numpy(); scores = trials.similarity.to_numpy()
    metrics = metrics_at_threshold(labels, scores, threshold); eer, eer_threshold = calculate_eer(labels, scores); metrics.update(eer=eer, eer_threshold=eer_threshold, roc_auc=float(roc_auc_score(labels, scores)))
    (out / "eer.json").write_text(json.dumps({"eer": eer, "eer_threshold": eer_threshold}, indent=2)); trials.to_csv(out / "verification_trials.csv", index=False)
    analysis = analyze_thresholds(labels, scores); analysis.to_csv(out / "threshold_analysis.csv", index=False)
    far, tar, _ = roc_curve(labels, scores); frr = 1 - tar
    plt.figure(); plt.plot(far, tar); plt.xlabel("False Accept Rate"); plt.ylabel("True Accept Rate"); plt.tight_layout(); plt.savefig(out / "speaker_roc_curve.png"); plt.close()
    plt.figure(); plt.plot(far, frr); plt.xlabel("False Accept Rate"); plt.ylabel("False Reject Rate"); plt.tight_layout(); plt.savefig(out / "det_curve.png"); plt.close()
    if "language" in trials and trials.language.notna().any():
        rows=[]
        for language, subset in trials.dropna(subset=["language"]).groupby("language"):
            y=(subset.trial_type=="genuine").astype(int).to_numpy(); values=subset.similarity.to_numpy(); row=metrics_at_threshold(y, values, threshold); row.update(language=language, num_trials=len(subset));
            try: row["EER"] = calculate_eer(y, values)[0]
            except ValueError: row["EER"] = None
            rows.append(row)
        pd.DataFrame(rows).to_csv(out / "language_results.csv", index=False)
    return metrics
