from pathlib import Path

from data_anonymizer.export_naming import default_export_path


def test_default_export_path_prefix():
    p = default_export_path(Path("samples/medical_patient_sample.xml"))
    assert p.name == "anonimizat_medical_patient_sample.xml"
    assert p.parent == Path("samples")
