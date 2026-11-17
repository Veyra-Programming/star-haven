# Haven (Heaven Language) Changelog

Release history for **Haven**, the official companion programming language for the **Open Digital Continuity Standard (ODCS)**.

---

## [v2.0.0] — 2026-11-12 — Natural-English Syntax & Continuity VM

### Added
- **Zero-Dependency Transpiler & CLI (`heaven/haven_lang.py`)**:
  - New `run`, `compile`, `lint`, and `repl` subcommands (`python heaven/haven_lang.py run script.hvn`).
  - Full `HAVEN_PRELUDE` standard runtime providing `PNCounter`, `ContinuityLedger`, `ZeroIntentLoss`, `TelemetryProbe`, `DurableRecord`, `seal_hash`, `crypto.sha256`, `merkle_root`, `uuid7`, `trim`, `uppercase`, and `String`.
- **Normal English Programming Constructs**:
  - Readable variable bindings: `set name to "Node"`, `let count be 3`, `remember region as "APAC"`.
  - Natural numeric updates: `increase count by 2`, `decrease quota by 1`.
  - Readable loops & branching: `repeat 4 times:` (with automatic 1-based `iteration`), `for each item in items:`, `whenever ...:`, `unless ...:`, `otherwise if ...:`, `otherwise:`, `until ...:`.
  - English comparisons & literals: `is equal to`, `is not equal to`, `is greater than`, `is less than`, `is at least`, `is at most`, `true`, `false`, `nothing`.
  - Smart output & interpolation: `say "Node {node_id} synced at {rtt}ms"` automatically upgrades `{...}` expressions inside string literals.
- **Advanced Continuity Syntax**:
  - **Multi-Line Pipelining (`|>` with `_`)**: Chain `"  data  " |> trim(_) |> uppercase(_) |> seal_hash(_) |> show(_)` cleanly across lines.
  - **Immutable Durable Records (`durable record`)**: Declares frozen dataclasses with automatic SHA-256 `.odcs_hash()`, `.to_dict()`, and `ContinuityImmutabilityError` on mutation attempts, plus colon-named constructor syntax (`Packet(tx_id: "...")`).
  - **Native ZIL Intent Preservation**: `preserve intent "<action>" with <payload> as receipt`.
  - **Clean Recovery Blocks**: `on error as err:` and `recover:`.
  - **Native C PEGEN Grammar Upgrade (`G:\Heaven Language\Grammar\python.gram` & `Parser\action_helpers.c`)**: Rebuilt `PCbuild\amd64\haven.exe` (`0 Warning(s), 0 Error(s)`) with native C support for `say`, `show`, `increase ... by`, `decrease ... by`, `remember ... as`, `whenever`, `otherwise if`, `otherwise`, `give back`, `ensure ... otherwise/because`, `recover`, `recover as err:`, `preserve ... as ... into`, and `forever:`.
  - **Specification & Examples**:
  - Published [HAVEN-SPEC.md](HAVEN-SPEC.md) and updated [README.md](README.md).
  - Added 5 runnable sample programs in `heaven/examples/` (`01_hello_english.hvn` to `05_adaptive_telemetry.hvn`).
- **Backend & Web Playground Integration**:
  - Upgraded `server/runtimes/haven_sandbox.py` so `/api/v1/haven/execute` transpiles and runs Haven v2.0 scripts safely inside the Python VM.
  - Upgraded `website/src/components/HavenPlayground.jsx` with Natural English presets and a toggleable **English Syntax Guide**.

### Fixed
- Fixed missing trailing comma after the `ai` preset in `heaven/js/heaven.js`.

---

## [v1.0.0] — 2026-10-15 — Universal 20-OS Binary Distribution

- Released compiled binary installers and archives across Windows (x64, ARM64, Portable, CLI), Linux (x86_64, ARM64, AppImage, `.deb`, `.rpm`, Arch `.pkg.tar.zst`), macOS (Universal, Apple Silicon, Intel), FreeBSD, Android ARM64/APK, and WebAssembly (`haven-runtime.wasm`).
- Published `downloads/downloads_manifest.json` with verified SHA-256 digests and file sizes.

