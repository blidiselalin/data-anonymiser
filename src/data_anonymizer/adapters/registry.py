"""Adapter registry — detect format and construct the right adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Type

from data_anonymizer.adapters.base import DataFormatAdapter
from data_anonymizer.adapters.xml_adapter import XmlAdapter

_ADAPTERS: list[Type[DataFormatAdapter]] = [
    XmlAdapter,
    # Future: CsvAdapter, JsonAdapter, ExcelAdapter
]


def register_adapter(adapter_cls: Type[DataFormatAdapter]) -> None:
    if adapter_cls not in _ADAPTERS:
        _ADAPTERS.insert(0, adapter_cls)


def list_supported_extensions() -> list[str]:
    exts: list[str] = []
    for cls in _ADAPTERS:
        exts.extend(cls.extensions)
    return sorted(set(exts))


def detect_format(path: Path) -> str | None:
    path = Path(path)
    for cls in _ADAPTERS:
        if cls.supports(path):
            return cls.format_id
    return None


def adapter_for_path(path: Path) -> DataFormatAdapter:
    path = Path(path)
    for cls in _ADAPTERS:
        if cls.supports(path):
            return cls()
    supported = ", ".join(list_supported_extensions())
    raise ValueError(f"Unsupported file format: {path.suffix or path.name}. Supported: {supported}")


def open_document(path: Path) -> DataFormatAdapter:
    adapter = adapter_for_path(path)
    adapter.load(path)
    return adapter
