from data_anonymizer.method_guidance import (
    METHOD_DISPLAY_ORDER,
    METHOD_INFO,
    method_select_options,
    select_label,
    select_tooltip,
)


def test_ui_methods_count():
    assert len(METHOD_INFO) == 4
    assert METHOD_DISPLAY_ORDER == ("redact", "pseudonym", "hash", "mask")


def test_select_label():
    assert select_label("redact") == "Eliminare"


def test_select_tooltip():
    assert "salt" in select_tooltip("hash").lower()


def test_method_select_options():
    assert set(method_select_options().values()) == {
        "Eliminare",
        "Pseudonim",
        "Amprentă (hash)",
        "Mascare",
    }
