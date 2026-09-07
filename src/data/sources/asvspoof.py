"""Bounded ASVspoof 2019 LA intake using Hugging Face's public row API."""
from __future__ import annotations

import hashlib
import json
import random
from typing import Any, Iterable

from .base import SourceRecord


class ASVspoofSource:
    """Adapter for the official ASVspoof 2019 LA evaluation mirror.

    The repository stores large embedded-audio Parquet shards. Its public row
    API provides a protocol-labelled row and an expiring URL for each individual
    FLAC file, allowing a bounded intake without downloading an entire shard.
    """

    repository = "SpeechAntiSpoofingBenchmarks/ASVspoof2019_LA"
    source_url = "https://huggingface.co/datasets/SpeechAntiSpoofingBenchmarks/ASVspoof2019_LA"
    rows_url = "https://datasets-server.huggingface.co/rows"
    source_dataset = "ASVspoof"
    track = "ASVspoof 2019 Logical Access (LA), evaluation partition"
    default_language = "english"

    def __init__(self) -> None:
        self.split_name = "test"
        self.audio_column = "audio"
        self.label_column = "label"
        self.label_mapping: dict[int, int] = {}
        self.original_labels: dict[int, str] = {}
        self.total_rows = 0

    @staticmethod
    def _classify_label(name: str) -> int | None:
        """Map only ASVspoof's documented binary protocol labels."""
        value = name.strip().lower()
        if value == "bonafide":
            return 0
        if value == "spoof":
            return 1
        return None

    @staticmethod
    def _notes(row: dict[str, Any]) -> dict[str, Any]:
        value = row.get("notes")
        if not isinstance(value, str):
            return {}
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _request_rows(self, offset: int, length: int) -> dict[str, Any]:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("The optional dependency 'requests' is required for bounded ASVspoof intake.") from exc
        response = requests.get(self.rows_url, params={"dataset": self.repository, "config": "default", "split": self.split_name, "offset": offset, "length": length}, timeout=60)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
            raise ValueError("ASVspoof row API returned an unexpected payload.")
        return payload

    def inspect(self, streaming: bool = True) -> dict[str, Any]:
        # `streaming` is retained for the common adapter interface; requests are
        # intrinsically bounded to 100 metadata rows and one selected audio file.
        payload = self._request_rows(offset=0, length=1)
        features = {str(feature.get("name")): feature.get("type", {}) for feature in payload.get("features", []) if isinstance(feature, dict)}
        audio = features.get(self.audio_column, {})
        label = features.get(self.label_column, {})
        names = list(label.get("names", [])) if isinstance(label, dict) else []
        mapping = {index: self._classify_label(name) for index, name in enumerate(names)}
        if audio.get("_type") != "Audio" or label.get("_type") != "ClassLabel" or set(mapping.values()) != {0, 1}:
            raise ValueError(f"Unsupported ASVspoof runtime schema: audio={audio}, labels={names}; expected Audio and exactly bonafide/spoof.")
        self.label_mapping = {index: value for index, value in mapping.items() if value is not None}
        self.original_labels = {index: name for index, name in enumerate(names)}
        self.total_rows = int(payload.get("num_rows_total") or 0)
        if self.total_rows <= 0:
            raise ValueError("ASVspoof row API reported no records.")
        return {
            "repository": self.repository, "source_url": self.source_url, "source_dataset": self.source_dataset,
            "track": self.track, "split": self.split_name, "streaming": streaming,
            "access_method": "Hugging Face public datasets-server row API with individual cached FLAC URLs",
            "features": {name: str(value) for name, value in features.items()}, "audio_column": self.audio_column,
            "label_column": self.label_column, "source_labels": names,
            "voiceguard_label_mapping": {str(index): self.label_mapping[index] for index in sorted(self.label_mapping)},
            "num_rows_total": self.total_rows, "license": "",
            "license_note": "ODC-By 1.0 is declared by the public mirror; retain LICENSE_REVIEW_REQUIRED until project use is approved.",
        }

    def _record_from_row(self, row: dict[str, Any], audio: dict[str, Any]) -> SourceRecord:
        source_value = int(row[self.label_column])
        if source_value not in self.label_mapping:
            raise ValueError("ASVspoof row has a label absent from the inspected schema.")
        notes = self._notes(row)
        reference = str(row.get("path") or notes.get("utterance_id") or "unknown")
        digest = hashlib.sha256(f"{self.repository}:{self.split_name}:{reference}".encode("utf-8")).hexdigest()[:20]
        speaker_id = str(notes.get("speaker_id") or f"source_{digest[:12]}")
        label = self.label_mapping[source_value]
        generator_family = str(notes["system_id"]) if label == 1 and notes.get("system_id") else "unknown"
        return SourceRecord(
            sample_id=f"asv19la_{digest}", original_label=self.original_labels[source_value], voiceguard_label=label,
            audio=audio, source_dataset=self.source_dataset, source_split=self.split_name,
            speaker_id=speaker_id, language=self.default_language, generator_family=generator_family if label == 1 else None,
            reference=reference, metadata={"track": self.track, "notes": notes, "original_extension": "flac"},
        )

    @staticmethod
    def _audio_url(row: dict[str, Any]) -> str | None:
        entries = row.get("audio")
        if not isinstance(entries, list) or not entries or not isinstance(entries[0], dict):
            return None
        value = entries[0].get("src")
        return str(value) if value else None

    def iter_records(self, seed: int, buffer_size: int) -> Iterable[SourceRecord]:
        if not self.label_mapping or self.total_rows <= 0:
            raise RuntimeError("Call inspect() successfully before iterating source records.")
        # Metadata rows are small; fetch the API's maximum page size. Audio is
        # intentionally left lazy so the caller downloads only records that
        # pass its balanced selection and duplicate checks.
        page_size = 100
        page_offsets = list(range(0, self.total_rows, page_size))
        random.Random(seed).shuffle(page_offsets)
        for offset in page_offsets:
            payload = self._request_rows(offset=offset, length=page_size)
            for item in payload["rows"]:
                if not isinstance(item, dict) or not isinstance(item.get("row"), dict):
                    continue
                row = item["row"]
                if int(row.get(self.label_column, -1)) not in self.label_mapping:
                    continue
                audio_url = self._audio_url(row)
                if not audio_url:
                    continue
                yield self._record_from_row(row, {"url": audio_url})
