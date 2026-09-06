from __future__ import annotations
import argparse, sys
from pathlib import Path
import pandas as pd, yaml
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.data.splitter import split_dataset

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--config", default=str(ROOT / "configs/preprocessing.yaml")); args = parser.parse_args()
    cp = Path(args.config).resolve(); cfg = yaml.safe_load(cp.read_text()); base = cp.parent.parent
    md = Path(cfg["dataset"]["metadata_dir"]); md = md if md.is_absolute() else base / md
    frame = pd.read_csv(md / "raw_metadata.csv"); s = cfg["split"]
    result = split_dataset(frame, s["train"], s["validation"], s["test"], s["random_seed"])
    result.to_csv(md / "file_splits.csv", index=False); print(result["split"].value_counts())

if __name__ == "__main__": main()
