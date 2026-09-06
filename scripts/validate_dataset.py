from __future__ import annotations
import argparse, logging, sys
from pathlib import Path
import pandas as pd, yaml
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.data.scanner import scan_dataset
from src.data.validator import validate_audio

def main() -> None:
    parser = argparse.ArgumentParser(description="Validate raw audio without modifying it")
    parser.add_argument("--config", default=str(ROOT / "configs/preprocessing.yaml")); args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    cp = Path(args.config).resolve(); cfg = yaml.safe_load(cp.read_text(encoding="utf-8")); base = cp.parent.parent
    raw_dir = Path(cfg["dataset"]["raw_dir"]); raw_dir = raw_dir if raw_dir.is_absolute() else base / raw_dir
    md = Path(cfg["dataset"]["metadata_dir"]); md = md if md.is_absolute() else base / md; md.mkdir(parents=True, exist_ok=True)
    raw_csv = md / "raw_metadata.csv"
    raw = pd.read_csv(raw_csv) if raw_csv.exists() else scan_dataset(raw_dir)
    report = pd.DataFrame([validate_audio(path, cfg.get("validation")) for path in tqdm(raw["file_path"], desc="Validating")])
    report.to_csv(md / "validation_report.csv", index=False)
    counts = report["status"].value_counts()
    print(f"Valid: {counts.get('VALID', 0)}  Warnings: {counts.get('WARNING', 0)}  Invalid: {counts.get('INVALID', 0)}")

if __name__ == "__main__": main()
