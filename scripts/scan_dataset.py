from __future__ import annotations
import argparse, logging, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.scanner import scan_dataset

def main() -> None:
    parser = argparse.ArgumentParser(description="Scan labelled raw audio")
    parser.add_argument("--config", default=str(ROOT / "configs/preprocessing.yaml"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    cfg_path = Path(args.config).resolve()
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    project = cfg_path.parent.parent
    raw = Path(cfg["dataset"]["raw_dir"]); raw = raw if raw.is_absolute() else project / raw
    out = Path(cfg["dataset"]["metadata_dir"]); out = out if out.is_absolute() else project / out
    out.mkdir(parents=True, exist_ok=True)
    frame = scan_dataset(raw); frame.to_csv(out / "raw_metadata.csv", index=False)
    print(f"Scanned {len(frame)} files -> {out / 'raw_metadata.csv'}")

if __name__ == "__main__": main()
