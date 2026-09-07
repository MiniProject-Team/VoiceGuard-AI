"""Source-neutral records for public audio dataset ingestion."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol


@dataclass(frozen=True)
class SourceRecord:
    sample_id: str
    original_label: str
    voiceguard_label: int
    audio: Any
    source_dataset: str
    source_split: str
    speaker_id: str | None = None
    language: str = "english"
    generator_family: str | None = None
    reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DatasetSource(Protocol):
    def inspect(self, streaming: bool) -> dict[str, Any]: ...
    def iter_records(self, seed: int, buffer_size: int) -> Iterable[SourceRecord]: ...
