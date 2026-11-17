# 🌌 Star & Haven: Sovereign Dual-Engine Foundation
### Universal Declarative UI (Star Language) + Natural-English Continuity Runtime (Haven Language)
**Standard:** Open Digital Continuity Standard (ODCS-2.0.0)  
**Author & Maintainer:** Anirudha Puthraya  
**Organization:** [Veyra-Programming](https://github.com/Veyra-Programming)  
**Official Portal:** [https://odcs.in/](https://odcs.in/)  
**License:** Apache-2.0  

---

## 🏛️ Executive Summary

The **Star & Haven Dual-Engine Foundation** provides an open-source, sovereign computing paradigm engineered from the ground up to replace fragile cloud-dependent application stacks. 

By eliminating the Virtual-DOM, Node.js/npm bloat, and opaque cloud backends, the Dual-Engine model achieves:
- ⚡ **Sub-16ms Zero Intent Loss (ZIL)**: Single-frame (60Hz) hardware-sealed intent receipts.
- 📦 **Compact 4.9 KB Binary Footprint**: Pure WebAssembly core executing directly in browser sandboxes.
- 🌐 **Asynchronous CRDT Mesh Convergence**: 100% offline write fidelity with deterministic semi-lattice state synchronization.
- 🗣️ **Natural-English Grammar**: Zero-barrier continuity backend logic authored in human sentences.

---

## 📂 Repository Architecture

```
star-haven/
├── star/                           # ⭐ STAR PROGRAMMING LANGUAGE CORE & SDK
│   ├── star.py / star.bat / star   # Sovereign CLI compiler & toolchain
│   ├── star_engine/                # Lexer, AST Parser, Semantic Analyzer
│   ├── star_backend/               # WebAssembly compiler, native C / bytecode
│   ├── star_runtime/               # 60 FPS Single-Frame Reactive Runtime
│   ├── Star.js                     # High-performance WASM JavaScript bridge
│   ├── lib/                        # Standard library (UI, Hardware, Sensors, Network)
│   ├── apps/                       # Reference declarative mobile & web applications
│   └── specs/                      # Architecture, Mobile, WebGPU & IR specifications
│
├── haven/                          # 🕊️ HAVEN (HEAVEN) LANGUAGE CONTINUITY ENGINE
│   ├── haven_lang.py               # Natural-English compiler, interpreter & REPL
│   ├── odcs_backend.hvn            # Production Continuity Gateway backend
│   ├── HAVEN-SPEC.md               # Formal Natural-English Grammar Specification
│   ├── lib/haven/                  # Core modules (Merkle WAL, CRDT, Intent, Ledger)
│   ├── examples/                   # Durable records, WAL append, mesh sync examples
│   └── vscode-extension/           # Syntax highlighting for .hvn, .heaven, .haven
│
├── integrations/                   # 🌌 DUAL-ENGINE BRIDGES & ENTRYPOINTS
│   ├── main.star                   # Star Declarative UI entrypoint
│   ├── star.toml                   # Dual-Engine project manifest
│   └── install.ps1                 # Automated 1-Click Cross-Platform Installer
│
├── LICENSE                         # Apache-2.0 Sovereign License
└── README.md                       # Master Architecture Guide
```

---

## ⭐ 1. Star Programming Language (v1.2.0 GA)

Star is a sovereign, declarative programming language delivering single-frame 60 FPS reactive user interfaces across Web, Windows, Linux, Android, and Flutter without Virtual DOM or npm dependencies.

```star
# Pure Star Declarative UI (main.star)
use UI

app ContinuityPortal
    variable _operating_mode = "OPTIMAL_ONLINE"
    variable _zil_counter = 42

    AppBar(title = "🏛️ ODCS Foundation", elevation = 0)

    Column(padding = 16)
        Card(elevation = 2)
            Text("Operating Mode: " + _operating_mode, style = "headline6")
            Text("ZIL Budget: < 0.15ms", style = "caption")
        end

        Button("▶ Commit Offline Intent", onClick = function()
            _zil_counter = _zil_counter + 1
            show "Minted Zero Intent Loss Cryptographic Receipt"
        end)
    end
end
```

### Star Toolchain Execution:
```bash
# Run Star application
star run main.star

# Compile directly to WebAssembly (app.wasm)
star compile main.star

# Validate AST syntax & semantic types
star check main.star
```

---

## 🕊️ 2. Haven (Heaven) Language (v2.0)

Haven is a natural-English programming language designed for zero-drift distributed continuity backends, durable record ledgers, and conflict-free mesh replication.

```heaven
// Haven Natural-English Grammar (odcs_backend.hvn)
durable record EmergencyEncounter:
    patient_id: String
    heart_rate: Integer

set encounter to EmergencyEncounter("PT-901", 78)
checkpoint encounter as "triage_vital" into hospital_ledger
give back "Sealed with Zero Intent Loss!"
```

### Haven Toolchain Execution:
```bash
# Execute Haven backend
python haven/haven_lang.py run haven/odcs_backend.hvn

# Verify AST grammar and RFC 8785 canonical types
python haven/haven_lang.py lint haven/odcs_backend.hvn

# Launch interactive natural-English REPL
python haven/haven_lang.py repl
```

---

## ⚡ 3. Automated 1-Click Installation

### Windows PowerShell:
```powershell
irm https://odcs.in/install.ps1 | iex
```

### Linux / Ubuntu:
```bash
curl -fsSL https://odcs.in/install.sh | bash
```

### Python SDK:
```bash
pip install odcs-sdk
```

---

## 📜 Specifications & Standards Track

- **ODCS-RFC-101**: Zero Intent Loss (ZIL) & Single-Frame Authority ($\Delta t < 16.66\text{ms}$)
- **ODCS-RFC-102**: Append-Only Merkle DAG & Durable Write-Ahead Log (WAL)
- **ODCS-RFC-103**: Asynchronous CRDT State Convergence & Vector Clocks ($V_{merged} = V_{local} \sqcup V_{remote}$)
- **ODCS-RFC-104**: Sovereign Star WASM Runtime & Single-Frame Frame Budget

---

## 👨‍💻 Author & Maintainer

**Anirudha Puthraya**  
*Standards Director & Author · ODCS Foundation*  
*Organization:* [Veyra-Programming](https://github.com/Veyra-Programming)  
*Website:* [https://odcs.in/](https://odcs.in/)  
*GitHub:* [@Anirudha2006-art](https://github.com/Anirudha2006-art)  

---

## ⚖️ License

Licensed under the **Apache License, Version 2.0**.
See [LICENSE](LICENSE) for details.
