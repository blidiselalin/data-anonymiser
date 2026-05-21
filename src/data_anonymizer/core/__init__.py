"""Format-agnostic anonymization engine."""

from data_anonymizer.core.methods import AnonymizeMethod, apply_method, list_methods
from data_anonymizer.core.rules import FieldRule, method_options_for

__all__ = [
    "AnonymizationSession",
    "AnonymizeMethod",
    "FieldRule",
    "apply_method",
    "list_methods",
    "method_options_for",
]


def __getattr__(name: str):
    if name == "AnonymizationSession":
        from data_anonymizer.core.engine import AnonymizationSession

        return AnonymizationSession
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
