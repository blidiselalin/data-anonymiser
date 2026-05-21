"""Format-agnostic data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FieldInfo:
    """Discovered anonymizable field (column, tag, path, etc.)."""

    field_id: str
    count: int
    sample_values: list[str] = field(default_factory=list)
    max_samples: int = 3

    @property
    def tag(self) -> str:
        """Alias for ``field_id`` (XML element name)."""
        return self.field_id

    def add_sample(self, text: str | None) -> None:
        if text is None:
            return
        stripped = text.strip()
        if not stripped or stripped in self.sample_values:
            return
        if len(self.sample_values) < self.max_samples:
            self.sample_values.append(stripped)
