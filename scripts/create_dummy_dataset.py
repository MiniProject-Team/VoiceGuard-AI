"""Create synthetic pipeline-test WAVs. These are not training data."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]

def _tone(sample_rate: int, duration: float, frequency: float, channels: int) -> np.ndarray:
    time = np.arange(round(sample_rate * duration), dtype=np.float32) / sample_rate
    mono = (.12 * np.sin(2 * np.pi * frequency * time)).astype(np.float32)
    return np.column_stack((mono, mono * .85)) if channels == 2 else mono

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate six synthetic pipeline-test files (not training data)")
    parser.add_argument("--output", type=Path, default=ROOT / "data/raw"); args = parser.parse_args()
    specs = {
        "real": [(8000, 6., 220., 1), (16000, 3., 260., 1), (44100, 7., 300., 2)],
        "fake": [(22050, 6., 330., 1), (16000, 4., 370., 2), (8000, 8., 410., 1)],
    }
    for label, items in specs.items():
        directory = args.output / label; directory.mkdir(parents=True, exist_ok=True)
        for index, (sr, duration, frequency, channels) in enumerate(items, 1):
            sf.write(directory / f"{label}_{index:03d}.wav", _tone(sr, duration, frequency, channels), sr)
    print(f"Created 6 synthetic TEST files under {args.output}. Do not use them for training.")

if __name__ == "__main__": main()
