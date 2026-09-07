"""Public-dataset source adapters used by the Phase 3 intake workflow."""

from .inthewild import InTheWildSource
from .asvspoof import ASVspoofSource

SOURCES = {"inthewild": InTheWildSource, "asvspoof": ASVspoofSource}


def create_source(name: str):
    try:
        return SOURCES[name.lower()]()
    except KeyError as exc:
        raise ValueError(f"Unsupported dataset source: {name}. Available: {', '.join(sorted(SOURCES))}") from exc
