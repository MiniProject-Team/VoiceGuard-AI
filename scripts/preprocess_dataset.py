from __future__ import annotations
import argparse, json, logging, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.pipeline import run_pipeline

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the VoiceGuard Phase 2 pipeline")
    parser.add_argument("--config", default=str(ROOT / "configs/preprocessing.yaml"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    print(json.dumps(run_pipeline(args.config, args.dry_run), indent=2))

if __name__ == "__main__": main()
