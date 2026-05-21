# PyInstaller — Windows desktop build
#   pyinstaller packaging/data_anonymizer.spec

from pathlib import Path

root = Path(SPECPATH).resolve().parent
src = root / "src"

a = Analysis(
    [str(src / "data_anonymizer" / "desktop" / "app.py")],
    pathex=[str(src)],
    binaries=[],
    datas=[(str(root / "samples"), "samples")],
    hiddenimports=[
        "data_anonymizer.adapters.xml_adapter",
        "data_anonymizer.desktop.main_window",
        "data_anonymizer.method_guidance",
        "data_anonymizer.export_naming",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DataAnonymizer",
    debug=False,
    console=False,
    icon=None,
)
