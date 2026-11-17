# Haven Language v2.0 Specification & Quick-Start Guide

**Haven (Heaven Language)** is the official companion programming language for the **Open Digital Continuity Standard (ODCS)**. It is engineered so anyone can read and write resilient, offline-first software like **normal English**, while offering **advanced functional pipelines, immutable cryptographic records, and CRDT primitives** built directly into the syntax.

---

## 1. Normal English Core (Easy to Write & Remember)

Every common control-flow and variable construct has an intuitive English form:

| Concept | Haven Natural English | Traditional Equivalent |
| :--- | :--- | :--- |
| Bind Variable | `set node to "BLR-Edge"` / `let port be 8000` / `remember key as "abc"` | `node = "BLR-Edge"` |
| Update Number | `increase count by 5` / `decrease quota by 1` | `count += 5` |
| Output | `say "Hello {node}"` / `show status` / `print "OK"` | `print(f"Hello {node}")` |
| Repeat Loop | `repeat 4 times:` (gives 1-based `iteration`) / `forever:` | `for iteration in range(1, 5):` / `while True:` |
| Iterate Collection | `for each peer in peers:` | `for peer in peers:` |
| Conditionals | `whenever rtt is less than 50:` / `unless offline:` / `otherwise if ...:` / `otherwise:` | `if rtt < 50:` / `if not offline:` / `elif ...:` / `else:` |
| Contracts & Checks | `ensure count >= 0 otherwise "Must be non-negative"` | `assert count >= 0, "Must be non-negative"` |
| Error Recovery | `try:` ... `recover as err:` / `recover:` | `try:` ... `except Exception as err:` |
| Until Loop | `until synced is equal to true:` | `while not (synced == True):` |
| Functions | `define check_health(node):` / `give back true` | `def check_health(node): return True` |
| Comments | `// Both C-style and # Python comments work` | `# comment` |
| Comparisons | `is equal to`, `is not equal to`, `is greater than`, `is less than`, `is at least`, `is at most` | `==`, `!=`, `>`, `<`, `>=`, `<=` |

---

## 2. Advanced Continuity Syntax

### A. Left-to-Right Pipelining (`|>`) with `_` Placeholder
Chain transformations cleanly from top to bottom without deeply nested parentheses:

```haven
"   alpha-telemetry-packet   "
    |> trim(_)
    |> uppercase(_)
    |> seal_hash(_)
    |> show(_)
```

### B. Durable Immutable Records (`durable record`)
Declare cryptographically verifiable, tamper-proof data structures in 4 lines:

```haven
durable record ContinuityPacket:
    tx_id: String
    guardian: String
    block_height: Integer

let packet = ContinuityPacket(tx_id: "TX-2026", guardian: "BLR-01", block_height: 1024)
say "Genesis Hash: {packet.odcs_hash()}"
```
Attempting to modify any field raises `ContinuityImmutabilityError`.

### C. Built-In Zero Intent Loss (`preserve intent`)
Stage user mutations locally with instant RFC 8785 / SHA-256 receipts:

```haven
preserve intent "DispatchMedicalSupply" with {"unit": "Ambulance-04", "oxygen": 2} as receipt
say "Receipt ID: {receipt['intent_id']}"
```

### D. Native Resilience Error Handling (`on error as err:`)
```haven
try:
    // risky operation
on error as err:
    say "Recovered locally: {err}"
```

---

## 3. Built-In Standard Library Globals
- **Strings**: `trim(s)`, `uppercase(s)`, `lowercase(s)`, `String(x)`
- **Cryptography**: `seal_hash(v)`, `crypto.sha256(v)`, `canonical_json(obj)`, `merkle_root(items)`, `uuid7()`, `now_ms()`
- **ODCS Layer 1–4**: `ContinuityLedger.open(uri)`, `PNCounter(node_id)`, `ZeroIntentLoss.preserve(...)`, `TelemetryProbe.classify(rtt_ms, battery_pct)`

