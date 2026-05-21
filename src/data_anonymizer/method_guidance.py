"""Romanian labels and tooltips for anonymization methods shown in the UI."""

from __future__ import annotations

from dataclasses import dataclass

METHOD_DISPLAY_ORDER = ("redact", "pseudonym", "hash", "mask")


@dataclass(frozen=True)
class MethodInfo:
    method: str
    title: str
    summary: str


METHOD_INFO: dict[str, MethodInfo] = {
    "redact": MethodInfo(
        method="redact",
        title="Eliminare",
        summary="Înlocuiește valoarea cu [anonimizat]. Cea mai sigură opțiune.",
    ),
    "pseudonym": MethodInfo(
        method="pseudonym",
        title="Pseudonim",
        summary="Cod stabil per valoare — util pentru legături între rânduri (necesită salt).",
    ),
    "hash": MethodInfo(
        method="hash",
        title="Amprentă (hash)",
        summary="Rezumat determinist; aceeași valoare produce mereu același cod (necesită salt).",
    ),
    "mask": MethodInfo(
        method="mask",
        title="Mascare",
        summary="Ascunde majoritatea caracterelor; păstrează ultimele (ex. ultimele 4 cifre).",
    ),
}


def select_label(method: str) -> str:
    return METHOD_INFO[method].title


def select_tooltip(method: str) -> str:
    return METHOD_INFO[method].summary


def method_select_options() -> dict[str, str]:
    return {m: select_label(m) for m in METHOD_DISPLAY_ORDER if m in METHOD_INFO}
