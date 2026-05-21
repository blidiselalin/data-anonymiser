"""Anonymization methods — format-agnostic value transforms."""

from __future__ import annotations

import hashlib
import re
from enum import Enum
from typing import Callable


ANONYMIZED_PLACEHOLDER = "[anonimizat]"


class AnonymizeMethod(str, Enum):
    REDACT = "redact"
    MASK = "mask"
    HASH = "hash"
    PSEUDONYM = "pseudonym"
    PARTIAL = "partial"
    CONSTANT = "constant"
    SHUFFLE_TOKEN = "shuffle_token"


def _redact(_: str, **__) -> str:
    return ANONYMIZED_PLACEHOLDER


def _mask(value: str, visible: int = 2, char: str = "*", **__) -> str:
    if not value:
        return value
    visible = max(0, min(visible, len(value)))
    return char * (len(value) - visible) + value[-visible:] if visible else char * len(value)


def _hash(value: str, salt: str = "", algorithm: str = "sha256", **__) -> str:
    digest = hashlib.new(algorithm, f"{salt}{value}".encode())
    return digest.hexdigest()[:16]


def _pseudonym(value: str, salt: str = "", namespace: str = "", **__) -> str:
    seed = f"{salt}:{namespace}:{value}".encode()
    token = hashlib.sha256(seed).hexdigest()[:12]
    return f"anon_{token}"


def _partial(value: str, keep_start: int = 1, keep_end: int = 1, char: str = "*", **__) -> str:
    if not value:
        return value
    keep_start = max(0, keep_start)
    keep_end = max(0, keep_end)
    if len(value) <= keep_start + keep_end:
        return char * len(value)
    end_slice = value[-keep_end:] if keep_end else ""
    middle = char * (len(value) - keep_start - keep_end)
    return value[:keep_start] + middle + end_slice


def _constant(_: str, replacement: str = ANONYMIZED_PLACEHOLDER, **__) -> str:
    return replacement


def _shuffle_token(value: str, salt: str = "", **__) -> str:
    parts = re.split(r"(\s+)", value)
    words = [p for p in parts if p and not p.isspace()]
    if len(words) < 2:
        return _pseudonym(value, salt=salt)

    keyed = sorted(
        enumerate(words),
        key=lambda item: hashlib.sha256(f"{salt}:{item[1]}".encode()).hexdigest(),
    )
    shuffled = [word for _, word in keyed]
    wi = 0
    out: list[str] = []
    for part in parts:
        if part.isspace():
            out.append(part)
        else:
            out.append(shuffled[wi])
            wi += 1
    return "".join(out)


_METHOD_REGISTRY: dict[AnonymizeMethod, Callable[..., str]] = {
    AnonymizeMethod.REDACT: _redact,
    AnonymizeMethod.MASK: _mask,
    AnonymizeMethod.HASH: _hash,
    AnonymizeMethod.PSEUDONYM: _pseudonym,
    AnonymizeMethod.PARTIAL: _partial,
    AnonymizeMethod.CONSTANT: _constant,
    AnonymizeMethod.SHUFFLE_TOKEN: _shuffle_token,
}


def apply_method(method: AnonymizeMethod | str, value: str, **options) -> str:
    key = AnonymizeMethod(method) if isinstance(method, str) else method
    fn = _METHOD_REGISTRY[key]
    return fn(value, **options)


def list_methods() -> list[str]:
    return [m.value for m in AnonymizeMethod]
