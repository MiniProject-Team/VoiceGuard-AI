from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "reports" / ".matplotlib"))
import matplotlib.pyplot as plt
import pandas as pd, yaml

def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect validation and processed metadata")
    parser.add_argument("--config", default=str(ROOT / "configs/preprocessing.yaml")); args = parser.parse_args()
    cp = Path(args.config).resolve(); cfg = yaml.safe_load(cp.read_text()); base = cp.parent.parent
    md = Path(cfg["dataset"]["metadata_dir"]); md = md if md.is_absolute() else base / md
    reports = Path(cfg["dataset"].get("reports_dir", "reports")); reports = reports if reports.is_absolute() else base / reports
    reports.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(md / "raw_metadata.csv") if (md / "raw_metadata.csv").exists() else pd.DataFrame()
    val = pd.read_csv(md / "validation_report.csv") if (md / "validation_report.csv").exists() else pd.DataFrame()
    proc = pd.read_csv(md / "processed_metadata.csv") if (md / "processed_metadata.csv").exists() else pd.DataFrame()
    dup = pd.read_csv(md / "duplicates.csv") if (md / "duplicates.csv").exists() else pd.DataFrame()
    summary = {"total_files": len(raw), "valid_files": int((val.get("status", pd.Series(dtype=str)) == "VALID").sum()),
               "invalid_files": int((val.get("status", pd.Series(dtype=str)) == "INVALID").sum()),
               "warnings": int((val.get("status", pd.Series(dtype=str)) == "WARNING").sum()),
               "real_files": int((raw.get("label_name", pd.Series(dtype=str)) == "real").sum()),
               "fake_files": int((raw.get("label_name", pd.Series(dtype=str)) == "fake").sum()),
               "real_fake_ratio": (float((raw.get("label_name", pd.Series(dtype=str)) == "real").sum()) /
                                   int((raw.get("label_name", pd.Series(dtype=str)) == "fake").sum())
                                   if int((raw.get("label_name", pd.Series(dtype=str)) == "fake").sum()) else None),
               "total_duration": float(val.get("duration", pd.Series(dtype=float)).sum()),
               "average_duration": float(val.get("duration", pd.Series(dtype=float)).mean()) if len(val) else None,
               "min_duration": float(val.get("duration", pd.Series(dtype=float)).min()) if len(val) else None,
               "max_duration": float(val.get("duration", pd.Series(dtype=float)).max()) if len(val) else None,
               "sample_rate_distribution": val.get("sample_rate", pd.Series(dtype=float)).value_counts().to_dict(),
               "channel_distribution": val.get("channels", pd.Series(dtype=float)).value_counts().to_dict(),
               "possible_duplicate_rows": len(dup), "generated_segments": len(proc),
               "split_counts": proc.get("split", pd.Series(dtype=str)).value_counts().to_dict()}
    print(json.dumps(summary, indent=2, default=str))
    plots = [(raw.get("label_name"), "Class distribution", "class_distribution.png"),
             (val.get("duration"), "Duration distribution", "duration_distribution.png"),
             (val.get("sample_rate"), "Sample-rate distribution", "sample_rate_distribution.png"),
             (proc.get("split"), "Split distribution", "split_distribution.png")]
    for series, title, filename in plots:
        if series is None or series.dropna().empty: continue
        plt.figure(figsize=(7, 4))
        if title == "Duration distribution": series.dropna().plot.hist(bins=30)
        else: series.value_counts().sort_index().plot.bar()
        plt.title(title); plt.tight_layout(); plt.savefig(reports / filename); plt.close()

if __name__ == "__main__": main()
