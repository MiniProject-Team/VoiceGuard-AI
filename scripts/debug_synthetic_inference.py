"""Diagnose Phase 3 scores using the same adapter as production inference."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.audio_utils import convert_to_mono, load_audio
from src.models.synthetic_preprocessing import waveform_statistics
from src.realtime.adapters import SyntheticDetectorAdapter


def main() -> None:
    parser = argparse.ArgumentParser(description="Print safe Phase 3 inference diagnostics for WAV/FLAC files.")
    parser.add_argument("audio", nargs="+", type=Path)
    parser.add_argument("--model", type=Path, default=ROOT / "models/best_model")
    args = parser.parse_args()
    detector = SyntheticDetectorAdapter(args.model)
    rows = []
    for path in args.audio:
        if not path.is_file():
            parser.error(f"Audio file does not exist: {path}")
        waveform, sample_rate = load_audio(path)
        mono = convert_to_mono(waveform)
        diagnostic = detector.diagnose(mono, sample_rate)
        row = {"filename": str(path), "source": waveform_statistics(mono, sample_rate), **diagnostic}
        rows.append(row)
        print(json.dumps(row, indent=2))
    probabilities = np.asarray([row["synthetic_probability"] for row in rows], dtype=float)
    print(json.dumps({"summary": {"count": int(probabilities.size), "minimum_synthetic_probability": float(probabilities.min()), "maximum_synthetic_probability": float(probabilities.max()), "mean_synthetic_probability": float(probabilities.mean()), "std_synthetic_probability": float(probabilities.std())}}, indent=2))


if __name__ == "__main__":
    main()
