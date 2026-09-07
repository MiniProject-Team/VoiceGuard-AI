"""Runtime-schema adapter for the Hugging Face InTheWild benchmark."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from .base import SourceRecord


class InTheWildSource:
    repository = "SpeechAntiSpoofingBenchmarks/InTheWild"
    source_url = "https://huggingface.co/datasets/SpeechAntiSpoofingBenchmarks/InTheWild"
    default_language = "english"

    def __init__(self) -> None:
        self.dataset: Any = None
        self.split_name: str | None = None
        self.audio_column: str | None = None
        self.label_column: str | None = None
        self.label_mapping: dict[int, int] = {}
        self.original_labels: dict[int, str] = {}

    @staticmethod
    def _classify_label(name: str) -> int | None:
        value = name.strip().lower().replace("_", "-")
        if any(token in value for token in ("bonafide", "bona-fide", "genuine", "real", "human")):
            return 0
        if any(token in value for token in ("spoof", "fake", "synthetic", "deepfake")):
            return 1
        return None

    def inspect(self, streaming: bool = True) -> dict[str, Any]:
        try:
            from datasets import Audio, ClassLabel, load_dataset
        except ImportError as exc:
            raise RuntimeError("The optional dependency 'datasets' is required; install requirements.txt.") from exc
        loaded = load_dataset(self.repository, streaming=streaming)
        if hasattr(loaded, "keys"):
            names = list(loaded.keys())
            if not names:
                raise ValueError("Source exposes no dataset splits.")
            self.split_name = "train" if "train" in names else names[0]
            dataset = loaded[self.split_name]
        else:
            self.split_name, dataset = "train", loaded
        features = dataset.features
        audio_fields = [name for name, feature in features.items() if isinstance(feature, Audio) or feature.__class__.__name__ == "Audio"]
        label_fields = [name for name, feature in features.items() if isinstance(feature, ClassLabel) or feature.__class__.__name__ == "ClassLabel"]
        if len(audio_fields) != 1 or len(label_fields) != 1:
            raise ValueError(f"Expected exactly one Audio and ClassLabel field; found audio={audio_fields}, labels={label_fields}")
        self.audio_column, self.label_column = audio_fields[0], label_fields[0]
        label_feature = features[self.label_column]
        names = list(getattr(label_feature, "names", []) or [])
        mapping = {index: self._classify_label(name) for index, name in enumerate(names)}
        if set(mapping.values()) != {0, 1}:
            raise ValueError(f"Unsupported source class labels {names}; expected one real/bonafide and one spoof/synthetic label.")
        self.label_mapping = {index: value for index, value in mapping.items() if value is not None}
        self.original_labels = {index: name for index, name in enumerate(names)}
        self.dataset = dataset.cast_column(self.audio_column, Audio(decode=False))
        return {
            "repository": self.repository,
            "source_url": self.source_url,
            "split": self.split_name,
            "streaming": streaming,
            "features": {name: str(feature) for name, feature in features.items()},
            "audio_column": self.audio_column,
            "label_column": self.label_column,
            "source_labels": names,
            "voiceguard_label_mapping": {str(index): self.label_mapping[index] for index in sorted(self.label_mapping)},
            "license": getattr(getattr(dataset, "info", None), "license", None),
        }

    @staticmethod
    def _note_metadata(row: dict[str, Any]) -> dict[str, Any]:
        candidate = row.get("notes")
        if not isinstance(candidate, str):
            return {}
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def iter_records(self, seed: int, buffer_size: int) -> Iterable[SourceRecord]:
        if self.dataset is None or self.audio_column is None or self.label_column is None or self.split_name is None:
            raise RuntimeError("Call inspect() successfully before iterating source records.")
        source = self.dataset.shuffle(seed=seed, buffer_size=buffer_size) if hasattr(self.dataset, "shuffle") else self.dataset
        for index, row in enumerate(source):
            source_value = int(row[self.label_column])
            if source_value not in self.label_mapping:
                continue
            note = self._note_metadata(row)
            reference = str(row.get("path") or note.get("utterance_id") or index)
            digest = hashlib.sha256(f"{self.repository}:{self.split_name}:{reference}".encode("utf-8")).hexdigest()[:20]
            speaker = note.get("speaker")
            speaker_id = str(speaker) if speaker else f"source_{digest[:12]}"
            original = self.original_labels[source_value]
            yield SourceRecord(sample_id=f"itw_{digest}", original_label=original, voiceguard_label=self.label_mapping[source_value], audio=row[self.audio_column], source_dataset="InTheWild", source_split=self.split_name, speaker_id=speaker_id, language=self.default_language, generator_family="unknown" if self.label_mapping[source_value] == 1 else None, reference=reference, metadata={"notes": note})
