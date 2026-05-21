# Data Anonymizer

Desktop app to anonymize **XML** files: pick fields, preview changes in memory, export a new file. The original is never modified.

Built with **Python 3.12+** and **PySide6**. The engine uses a small **adapter** layer so CSV, JSON, and Excel can be added later without rewriting the UI.

## Quick start

```bash
git clone https://github.com/blidiselalin/data-anonymiser.git
cd data-anonymiser

python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

pip install -e .
data-anonymizer
```

## How to use

1. **Open a file** — toolbar **Deschide**, menu **Fișier**, or a sample under **Exemple**.
2. **Select fields** — check the rows you want to anonymize (default: none selected).
3. **Choose a method** per row (enabled only when the row is checked):

   | Method | Label in UI | Result |
   |--------|-------------|--------|
   | `redact` | Eliminare | `[anonimizat]` |
   | `pseudonym` | Pseudonim | Stable code per value (uses **Salt**) |
   | `hash` | Amprentă (hash) | Deterministic digest (uses **Salt**) |
   | `mask` | Mascare | Hides all but the last characters |

4. **Preview** — **Previzualizare** (or `Ctrl+P`). Review the result in the right panel.
5. **Export** — after a successful preview, **Exportă fișier anonimizat** appears. Saves as `anonimizat_<original>.xml` next to the source by default.

Optional **Salt** (password field): required for pseudonym and hash; keep it secret and separate from exported files.

## Samples

Fictional Romanian test data (no real personal data):

- `samples/medical_patient_sample.xml`
- `samples/feed_sample.xml`

## Project layout

```
data-anonymizer/
├── src/data_anonymizer/
│   ├── adapters/          # Format plug-ins (XML today)
│   ├── core/              # Engine, rules, transform methods
│   ├── desktop/           # PySide6 UI
│   ├── export_naming.py   # Default export file names
│   └── method_guidance.py # UI labels for methods
├── samples/
├── packaging/             # PyInstaller spec (Windows .exe)
├── tests/
└── output/                # Local exports (gitignored)
```

## Build a Windows executable

```bash
pip install -e ".[build]"
pyinstaller packaging/data_anonymizer.spec
```

Output: `dist/DataAnonymizer.exe` (includes `samples/`).

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Roadmap

- [ ] CSV / JSON / Excel adapters
- [ ] Optional GDPR guidance panel (removed from v1 for a simpler UI)

## License

Proprietary — © Zenaios. Adjust before open-sourcing if needed.
