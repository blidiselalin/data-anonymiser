"""Format adapters — plug-in layer for XML, CSV, JSON, etc."""

from data_anonymizer.adapters.base import DataFormatAdapter
from data_anonymizer.adapters.registry import (
    adapter_for_path,
    detect_format,
    list_supported_extensions,
    open_document,
)

__all__ = [
    "DataFormatAdapter",
    "adapter_for_path",
    "detect_format",
    "list_supported_extensions",
    "open_document",
]
