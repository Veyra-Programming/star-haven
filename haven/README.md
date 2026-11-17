# Haven (Heaven Language) v2.0 — Directory & Toolchain

Welcome to the official **Haven Language** directory (`heaven/`), the companion programming language for the **Open Digital Continuity Standard (ODCS)**.

## Directory Structure

- `haven_lang.py` — Haven v2.0 Natural-English & Pipeline Transpiler + Native Continuity Runtime VM & CLI.
- `HAVEN-SPEC.md` — Complete syntax guide covering Normal English Core + Advanced ODCS Constructs.
- `examples/` — Runnable `.hvn` programs demonstrating Natural English, pipelines, `durable record`, CRDTs, and Zero Intent Loss.
- `downloads/` — Universal 20-OS binary distributions & SHA-256 manifest (`downloads_manifest.json`).
- `js/`, `css/`, `assets/` — Language portal assets & interactive presets.

## Quick Start via CLI

```bash
# Run any Haven (.hvn) script natively
python heaven/haven_lang.py run heaven/examples/01_hello_english.hvn

# Inspect transpiled Python output and run
python heaven/haven_lang.py run heaven/examples/04_continuity_mesh.hvn --show-compiled

# Transpile .hvn to Python only
python heaven/haven_lang.py compile heaven/examples/02_pipelines_and_crypto.hvn

# Validate Haven AST syntax
python heaven/haven_lang.py lint heaven/examples/03_durable_records.hvn

# Launch interactive Haven REPL
python heaven/haven_lang.py repl
```

