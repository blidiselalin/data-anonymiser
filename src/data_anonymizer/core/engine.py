"""Orchestrates adapters and rules — UI/CLI should depend on this, not on XML."""

from __future__ import annotations

from pathlib import Path

from data_anonymizer.adapters.base import DataFormatAdapter
from data_anonymizer.adapters.registry import detect_format, open_document
from data_anonymizer.core.rules import FieldRule
from data_anonymizer.models import FieldInfo


class AnonymizationSession:
    """In-memory working copy; source file on disk is never modified."""

    def __init__(self, adapter: DataFormatAdapter | None = None) -> None:
        self.adapter = adapter
        self._preview_applied = False
        self._last_changed = 0

    @classmethod
    def from_path(cls, path: str | Path) -> AnonymizationSession:
        adapter = open_document(Path(path))
        return cls(adapter)

    @property
    def source_path(self) -> Path | None:
        return self.adapter.source_path if self.adapter else None

    @property
    def format_id(self) -> str | None:
        return self.adapter.format_id if self.adapter else None

    def load(self, path: str | Path) -> str:
        path = Path(path)
        fmt = detect_format(path)
        if fmt is None:
            raise ValueError(f"Unsupported format: {path}")
        self.adapter = open_document(path)
        self._preview_applied = False
        self._last_changed = 0
        return fmt

    def fields(self) -> dict[str, FieldInfo]:
        self._require_adapter()
        return self.adapter.discover_fields()

    def header_snapshot(self) -> dict[str, list[str]]:
        self._require_adapter()
        return self.adapter.header_snapshot()

    def document_text(self) -> str:
        """Serialize the current in-memory document (original until preview/export)."""
        self._require_adapter()
        return self.adapter.to_text()

    def discard_preview(self) -> None:
        """Reload original from disk if a preview was applied in memory."""
        if self._preview_applied and self.source_path:
            self.adapter.reset_to_original()
            self._preview_applied = False

    def preview(self, rules: list[FieldRule], *, salt: str = "") -> tuple[int, str]:
        """Apply rules in memory and return (changed_count, text)."""
        self._require_adapter()
        if self._preview_applied and self.source_path:
            self.adapter.reset_to_original()
        count = self.adapter.anonymize(rules, salt=salt)
        self._preview_applied = True
        self._last_changed = count
        return count, self.adapter.to_text()

    def export(self, output_path: str | Path, rules: list[FieldRule], *, salt: str = "") -> int:
        """Write anonymized file to a new path; reloads original if preview was applied."""
        self._require_adapter()
        if self._preview_applied and self.source_path:
            self.adapter.reset_to_original()
        count = self.adapter.anonymize(rules, salt=salt)
        self.adapter.export(Path(output_path))
        self._preview_applied = False
        self._last_changed = count
        return count

    def _require_adapter(self) -> None:
        if self.adapter is None:
            raise RuntimeError("No document loaded")
