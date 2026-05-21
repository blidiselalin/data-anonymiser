"""Field rules — independent of file format."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from data_anonymizer.core.methods import AnonymizeMethod


@dataclass
class FieldRule:
    field_id: str
    method: AnonymizeMethod | str = AnonymizeMethod.REDACT
    options: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FieldRule:
        fid = data.get("field_id") or data.get("tag")
        if not fid:
            raise ValueError("Rule requires 'field_id'")
        return cls(
            field_id=fid,
            method=data.get("method", AnonymizeMethod.REDACT),
            options=data.get("options") or {},
        )


def method_options_for(method: str) -> dict[str, Any]:
    if method == "mask":
        return {"visible": 4, "char": "X"}
    if method == "partial":
        return {"keep_start": 1, "keep_end": 0}
    if method == "hash":
        return {"algorithm": "sha256"}
    return {}
