"""Default file names for anonymized exports."""

from __future__ import annotations

from pathlib import Path

EXPORT_PREFIX = "anonimizat_"


def default_export_path(source: Path | None) -> Path:
    """Return ``anonimizat_<original>.<ext>`` next to the source file."""
    if source is None:
        return Path(f"{EXPORT_PREFIX}output.xml")
    stem = source.stem
    if not stem.startswith(EXPORT_PREFIX):
        stem = f"{EXPORT_PREFIX}{stem}"
    return source.parent / f"{stem}{source.suffix}"
