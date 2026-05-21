"""Abstract adapter contract for input/output formats."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from data_anonymizer.models import FieldInfo

if TYPE_CHECKING:
    from data_anonymizer.core.rules import FieldRule


class DataFormatAdapter(ABC):
    """Read a document, discover fields, apply rules, export — without mutating the source file."""

    format_id: str
    display_name: str
    extensions: tuple[str, ...]

    def __init__(self) -> None:
        self._source_path: Path | None = None

    @property
    def source_path(self) -> Path | None:
        return self._source_path

    @classmethod
    @abstractmethod
    def supports(cls, path: Path) -> bool:
        """Return True if this adapter can handle the file."""

    @abstractmethod
    def load(self, path: Path) -> None:
        """Load document from disk (original file is never written)."""

    @abstractmethod
    def discover_fields(self, *, include_empty: bool = False) -> dict[str, FieldInfo]:
        """Return field_id → metadata for user selection."""

    def header_snapshot(self) -> dict[str, list[str]]:
        """Optional preview of header/metadata section (format-specific)."""
        return {}

    @abstractmethod
    def anonymize(self, rules: list[Any], *, salt: str = "", skip_empty: bool = True) -> int:
        """Apply rules in memory; return number of values changed."""

    @abstractmethod
    def to_text(self) -> str:
        """Serialize current in-memory document for preview."""

    @abstractmethod
    def export(self, path: Path) -> None:
        """Write anonymized document to a new path."""

    def reset_to_original(self) -> None:
        """Reload from source path after preview (discard in-memory changes)."""
        if self._source_path is None:
            raise RuntimeError("No source file loaded")
        self.load(self._source_path)
