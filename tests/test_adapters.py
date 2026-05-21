from pathlib import Path

import pytest

from data_anonymizer.adapters.registry import (
    adapter_for_path,
    detect_format,
    list_supported_extensions,
    open_document,
)
from data_anonymizer.core.engine import AnonymizationSession
from data_anonymizer.core.rules import FieldRule

SAMPLE = Path(__file__).resolve().parents[1] / "samples" / "feed_sample.xml"
MEDICAL = Path(__file__).resolve().parents[1] / "samples" / "medical_patient_sample.xml"


def test_detect_xml():
    assert detect_format(SAMPLE) == "xml"


def test_extensions_include_xml():
    assert ".xml" in list_supported_extensions()


def test_open_and_discover():
    doc = open_document(SAMPLE)
    fields = doc.discover_fields()
    assert "CHART_ARTIST" in fields
    assert fields["CHART_ARTIST"].count == 2


def test_session_preview_and_export(tmp_path: Path):
    session = AnonymizationSession.from_path(SAMPLE)
    rules = [FieldRule(field_id="BUSINESS_CONTACT_NAME", method="redact")]
    count, text = session.preview(rules, salt="x")
    assert count >= 1
    assert "[anonimizat]" in text
    assert "Jane Example" not in text

    out = tmp_path / "out.xml"
    session.export(out, rules, salt="x")
    assert out.read_text(encoding="utf-8").count("[anonimizat]") >= 1


def test_medical_header_snapshot():
    doc = open_document(MEDICAL)
    header = doc.header_snapshot()
    assert "PATIENT_NAME" in header or "FACILITY_NAME" in header
    assert "Spitalul" in header.get("FACILITY_NAME", [""])[0]


def test_unsupported_format(tmp_path: Path):
    bad = tmp_path / "data.xyz"
    bad.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        adapter_for_path(bad)
