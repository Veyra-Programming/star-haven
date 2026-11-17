#!/usr/bin/env python3
"""
Haven Language v2.0 — Natural-English & Advanced Continuity Transpiler + VM CLI
Companion Language for the Open Digital Continuity Standard (ODCS)

Provides:
  - Transpilation of Haven (.hvn) Natural-English & Advanced Pipeline syntax to Python 3.
  - Built-in ODCS Layer 1-4 runtime prelude (crypto, DurableRecord, PNCounter, ZIL, Ledger).
  - CLI commands: run, compile, lint, repl.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
import textwrap
import time
import uuid
from dataclasses import dataclass, field, is_dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


class HavenSyntaxError(SyntaxError):
    """Raised when Haven source cannot be cleanly lowered to executable AST."""


# ---------------------------------------------------------------------------
# Runtime Prelude injected before executing transpiled Haven programs
# ---------------------------------------------------------------------------

HAVEN_PRELUDE = '''
import dataclasses as _dc
import hashlib as _hashlib
import json as _json
import time as _time
import uuid as _uuid


class ContinuityImmutabilityError(Exception):
    """Raised when attempting to mutate a hardware-sealed ODCS durable record."""


def canonical_json(obj):
    if hasattr(obj, "to_dict"):
        obj = obj.to_dict()
    elif _dc.is_dataclass(obj):
        obj = _dc.asdict(obj)
    return _json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def seal_hash(value):
    if isinstance(value, str):
        raw = value.encode("utf-8")
    else:
        raw = canonical_json(value).encode("utf-8")
    return _hashlib.sha256(raw).hexdigest()


def merkle_root(items):
    if not items:
        return seal_hash("EMPTY_MERKLE_ROOT")
    level = [seal_hash(i) for i in items]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        next_level = []
        for idx in range(0, len(level), 2):
            next_level.append(_hashlib.sha256((level[idx] + level[idx + 1]).encode("utf-8")).hexdigest())
        level = next_level
    return level[0]


def uuid7():
    ts_ms = int(_time.time() * 1000) & ((1 << 48) - 1)
    rand_bytes = _uuid.uuid4().bytes
    b = bytearray(rand_bytes)
    b[0:6] = ts_ms.to_bytes(6, "big")
    b[6] = (b[6] & 0x0F) | 0x70
    b[8] = (b[8] & 0x3F) | 0x80
    return str(_uuid.UUID(bytes=bytes(b)))


def now_ms():
    return int(_time.time() * 1000)


class _HavenStr(str):
    """String subclass providing ergonomic Haven chain helpers (.trim, .to_uppercase)."""
    def trim(self):
        return _HavenStr(self.strip())

    def to_uppercase(self):
        return _HavenStr(self.upper())

    def to_lowercase(self):
        return _HavenStr(self.lower())


def trim(value):
    return _HavenStr(str(value).strip())


def uppercase(value):
    return _HavenStr(str(value).upper())


def lowercase(value):
    return _HavenStr(str(value).lower())


def String(value):
    return _HavenStr(str(value))


def Integer(value):
    return int(value)


class _CryptoMod:
    @staticmethod
    def sha256(value):
        return seal_hash(value)

    @staticmethod
    def verify(value, expected_hex):
        return seal_hash(value) == str(expected_hex).lower()


crypto = _CryptoMod()


class DurableRecord:
    """Base mixin for ODCS sealed immutable records."""
    def __setattr__(self, name, value):
        if getattr(self, "_sealed_lock", False):
            raise ContinuityImmutabilityError(
                f"Cannot mutate sealed field '{name}' on durable record {self.__class__.__name__}"
            )
        super().__setattr__(name, value)

    def __post_init__(self):
        object.__setattr__(self, "_sealed_lock", True)

    def to_dict(self):
        return {
            f.name: getattr(self, f.name)
            for f in _dc.fields(self)
        }

    def odcs_hash(self):
        return seal_hash(self.to_dict())

    def to_json(self):
        return canonical_json(self.to_dict())


class PNCounter:
    """ODCS Layer 2 Conflict-Free Replicated Positive-Negative Counter."""
    def __init__(self, node_id="local-node"):
        self.node_id = node_id
        self.p = {node_id: 0}
        self.n = {}

    def inc(self, amount=1):
        self.p[self.node_id] = self.p.get(self.node_id, 0) + amount
        return self

    def dec(self, amount=1):
        self.n[self.node_id] = self.n.get(self.node_id, 0) + amount
        return self

    def merge(self, other):
        rp = other.p if hasattr(other, "p") else other
        rn = other.n if hasattr(other, "n") else {}
        for k, v in rp.items():
            self.p[k] = max(self.p.get(k, 0), v)
        for k, v in rn.items():
            self.n[k] = max(self.n.get(k, 0), v)
        return self

    def value(self):
        return sum(self.p.values()) - sum(self.n.values())


class ZeroIntentLoss:
    """ODCS Layer 4 Zero Intent Loss local receipt minter & staging log."""
    _receipts = []

    @classmethod
    def preserve(cls, action, payload=None, actor="haven-runtime"):
        record = {
            "intent_id": "zil_" + uuid7().replace("-", "")[:16],
            "actor": actor,
            "action": str(action),
            "payload": payload if payload is not None else {},
            "timestamp_ms": now_ms(),
            "status": "STAGED_TO_WAL",
        }
        record["receipt_hash"] = seal_hash(record)
        cls._receipts.append(record)
        return record

    @classmethod
    def receipts(cls):
        return list(cls._receipts)


class ContinuityLedger:
    """ODCS Layer 1 append-only Merkle-chained ledger."""
    def __init__(self, uri="haven://local-wal"):
        self.uri = uri
        self.blocks = []
        self._append_raw({"event": "GENESIS", "uri": uri, "ts": now_ms()})

    @classmethod
    def open(cls, uri="haven://local-wal"):
        return cls(uri)

    def _append_raw(self, data):
        prev_hash = self.blocks[-1]["hash"] if self.blocks else "0" * 64
        payload = {"height": len(self.blocks), "prev_hash": prev_hash, "data": data}
        block_hash = seal_hash(payload)
        block = {"height": len(self.blocks), "prev_hash": prev_hash, "hash": block_hash, "data": data}
        self.blocks.append(block)
        return block

    def append(self, data):
        return self._append_raw(data)

    def current_height(self):
        return len(self.blocks)

    def genesis_hash(self):
        return self.blocks[0]["hash"]

    def merkle_root(self):
        return merkle_root([b["hash"] for b in self.blocks])

    def verify_integrity(self):
        for i, b in enumerate(self.blocks):
            expected_prev = self.blocks[i - 1]["hash"] if i > 0 else "0" * 64
            if b["prev_hash"] != expected_prev:
                return {"is_valid": False, "drift_height": i}
            recomputed = seal_hash({"height": b["height"], "prev_hash": b["prev_hash"], "data": b["data"]})
            if recomputed != b["hash"]:
                return {"is_valid": False, "drift_height": i}
        return {"is_valid": True, "height": len(self.blocks), "merkle_root": self.merkle_root()}


class TelemetryProbe:
    """ODCS Layer 3 Environmental Adaptation helper."""
    @staticmethod
    def classify(rtt_ms, battery_pct=100):
        if rtt_ms < 0:
            return "AIRGAP_OFFLINE"
        if rtt_ms > 350 or battery_pct < 15:
            return "CONSTRAINED_JITTER"
        return "OPTIMAL_ONLINE"


true = True
false = False
nothing = None
'''


HAVEN_TYPE_MAP = {
    "String": "str",
    "Integer": "int",
    "Float": "float",
    "Boolean": "bool",
    "List": "list",
    "Map": "dict",
    "Any": "Any",
}


def _split_strings_and_code(text: str) -> List[Tuple[bool, str]]:
    """Split a source line into [(is_string_literal, chunk)] preserving quotes/escapes."""
    parts: List[Tuple[bool, str]] = []
    buf: List[str] = []
    i = 0
    n = len(text)
    in_quote: Optional[str] = None
    is_triple = False

    while i < n:
        ch = text[i]
        if in_quote is None:
            if ch == "/" and i + 1 < n and text[i + 1] == "/":
                # Single-line // comment outside string: discard remainder
                break
            if ch == "#":
                # Python # comment outside string: keep untouched and stop scanning
                buf.append(text[i:])
                break
            if ch in ('"', "'"):
                if text[i:i + 3] == ch * 3:
                    if buf:
                        parts.append((False, "".join(buf)))
                        buf = []
                    in_quote = ch
                    is_triple = True
                    buf.append(ch * 3)
                    i += 3
                    continue
                if buf:
                    parts.append((False, "".join(buf)))
                    buf = []
                in_quote = ch
                is_triple = False
                buf.append(ch)
                i += 1
                continue
            buf.append(ch)
            i += 1
        else:
            buf.append(ch)
            if ch == "\\" and i + 1 < n:
                buf.append(text[i + 1])
                i += 2
                continue
            if is_triple and text[i:i + 3] == in_quote * 3:
                buf.append(in_quote * 2)
                parts.append((True, "".join(buf)))
                buf = []
                in_quote = None
                is_triple = False
                i += 3
                continue
            if not is_triple and ch == in_quote:
                parts.append((True, "".join(buf)))
                buf = []
                in_quote = None
                i += 1
                continue
            i += 1

    if buf:
        parts.append((in_quote is not None, "".join(buf)))
    return parts


def _auto_interpolate_string(parts: List[Tuple[bool, str]]) -> List[Tuple[bool, str]]:
    """Convert Haven strings containing `{identifier}` into Python f-strings cleanly."""
    interp_re = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*|\[[^\]]+\]|\([^)]*\))*\}")
    out: List[Tuple[bool, str]] = []
    for idx, (is_str, chunk) in enumerate(parts):
        if is_str and interp_re.search(chunk):
            # Avoid double-prefixing if preceding code already ends with f/r/b/u quote prefix
            prev_code = out[-1][1] if out and not out[-1][0] else ""
            if not re.search(r"[frbuFRBU]+$", prev_code):
                out.append((True, "f" + chunk))
                continue
        out.append((is_str, chunk))
    return out


def _replace_english_ops(code_chunk: str) -> str:
    """Translate natural-English comparison and value keywords outside string literals."""
    replacements = [
        (r"\bis\s+greater\s+than\s+or\s+equal\s+to\b", ">="),
        (r"\bis\s+at\s+least\b", ">="),
        (r"\bis\s+less\s+than\s+or\s+equal\s+to\b", "<="),
        (r"\bis\s+at\s+most\b", "<="),
        (r"\bis\s+not\s+equal\s+to\b", "!="),
        (r"\bis\s+equal\s+to\b", "=="),
        (r"\bis\s+greater\s+than\b", ">"),
        (r"\bis\s+less\s+than\b", "<"),
        (r"\btrue\b", "True"),
        (r"\bfalse\b", "False"),
        (r"\bnothing\b", "None"),
    ]
    res = code_chunk
    for pattern, target in replacements:
        res = re.sub(pattern, target, res)
    return res


def _convert_call_named_colons(expr: str) -> str:
    """Convert `fn(key: val, other: val2)` named args to Python `fn(key=val, other=val2)` without touching dicts `{k: v}`, comments, or lambdas."""
    out: List[str] = []
    stack: List[str] = []  # '(' or '[' or '{'
    i = 0
    n = len(expr)
    in_q: Optional[str] = None

    while i < n:
        ch = expr[i]
        if in_q:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(expr[i + 1])
                i += 2
                continue
            if ch == in_q:
                in_q = None
            i += 1
            continue

        if ch == "#":
            end_nl = expr.find("\n", i)
            if end_nl == -1:
                out.append(expr[i:])
                break
            out.append(expr[i:end_nl])
            i = end_nl
            continue

        if ch in ('"', "'"):
            in_q = ch
            out.append(ch)
            i += 1
            continue

        if ch in "([{":
            stack.append(ch)
            out.append(ch)
            i += 1
            continue

        if ch in ")]}":
            if stack:
                stack.pop()
            out.append(ch)
            i += 1
            continue

        # Inside (...) call arguments: transform `ident:` -> `ident=` (skip `lambda params:`)
        if stack and stack[-1] == "(":
            m_lam = re.match(r"lambda\b[^:\n]*:", expr[i:])
            if m_lam and (i == 0 or not (expr[i - 1].isalnum() or expr[i - 1] == "_")):
                out.append(m_lam.group(0))
                i += m_lam.end()
                continue
            m = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*:(?!:)", expr[i:])
            if m and (i == 0 or not (expr[i - 1].isalnum() or expr[i - 1] == "_")):
                out.append(f"{m.group(1)}=")
                i += m.end()
                continue

        out.append(ch)
        i += 1

    return "".join(out)


def _rewrite_parts(line: str) -> str:
    """Apply string stripping (//), auto-interpolation, and English ops cleanly."""
    parts = _split_strings_and_code(line)
    parts = _auto_interpolate_string(parts)
    rebuilt: List[str] = []
    for is_str, chunk in parts:
        if is_str:
            rebuilt.append(chunk)
        else:
            rebuilt.append(_replace_english_ops(chunk))
    return "".join(rebuilt).rstrip()


def _split_outside_strings(expr: str, sep: str = "|>") -> List[str]:
    """Split expression by top-level pipeline separator outside strings/brackets."""
    segments: List[str] = []
    buf: List[str] = []
    depth = 0
    in_q: Optional[str] = None
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]
        if in_q:
            buf.append(ch)
            if ch == "\\" and i + 1 < n:
                buf.append(expr[i + 1])
                i += 2
                continue
            if ch == in_q:
                in_q = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_q = ch
            buf.append(ch)
            i += 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}" and depth > 0:
            depth -= 1

        if depth == 0 and expr.startswith(sep, i):
            segments.append("".join(buf).strip())
            buf = []
            i += len(sep)
            continue

        buf.append(ch)
        i += 1

    segments.append("".join(buf).strip())
    return segments


def _substitute_placeholder(stage: str, lhs: str) -> str:
    """Substitute standalone `_` placeholder outside strings with `lhs`, or inject into call."""
    parts = _split_strings_and_code(stage)
    replaced_any = False
    new_parts: List[Tuple[bool, str]] = []
    for is_str, chunk in parts:
        if not is_str:
            updated, count = re.subn(r"(?<![a-zA-Z0-9_])_(?![a-zA-Z0-9_])", f"({lhs})", chunk)
            if count > 0:
                replaced_any = True
            new_parts.append((False, updated))
        else:
            new_parts.append((True, chunk))

    if replaced_any:
        return "".join(c for _, c in new_parts)

    # No explicit '_' placeholder: if call fn(...), insert as first argument; else call fn(lhs)
    m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_.]*)\((.*)\)$", stage.strip())
    if m:
        fn_name, args = m.group(1), m.group(2).strip()
        return f"{fn_name}({lhs}, {args})" if args else f"{fn_name}({lhs})"
    return f"{stage.strip()}({lhs})"


def _fold_pipeline(expr: str) -> str:
    """Compile Haven pipeline chains (`a |> fn(_) |> show(_)`) left-to-right."""
    if "|>" not in expr:
        return expr
    stages = _split_outside_strings(expr, "|>")
    if len(stages) < 2:
        return expr
    acc = stages[0]
    for stage in stages[1:]:
        if not stage:
            continue
        # Special English sink words at pipeline end
        if stage in ("show", "say", "print", "show(_)", "say(_)", "print(_)"):
            acc = f"print({acc})"
        else:
            acc = _substitute_placeholder(stage, acc)
    return acc


def is_pure_python(source: str) -> bool:
    """Return True if the source parses cleanly as standard Python and uses no Haven extensions."""
    try:
        ast.parse(source)
        return True
    except SyntaxError:
        return False


def _preprocess_multiline_pipelines(lines: List[str]) -> List[str]:
    """Attach continuation lines starting with `|>` onto the preceding expression line."""
    merged: List[str] = []
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("|>") and merged:
            # Find last non-empty line to append pipeline stage
            k = len(merged) - 1
            while k >= 0 and not merged[k].strip():
                k -= 1
            if k >= 0:
                merged[k] = merged[k].rstrip() + " " + stripped
                continue
        merged.append(raw)
    return merged


def transpile_haven(source: str, include_prelude: bool = True) -> str:
    """
    Transpile Haven (.hvn) Natural-English & Advanced Continuity syntax to Python 3.
    Preserves standard Python compatibility when given valid Python scripts.
    """
    lines = _preprocess_multiline_pipelines(source.splitlines())
    out_lines: List[str] = []
    i = 0
    n = len(lines)

    while i < n:
        raw_line = lines[i]
        indent_len = len(raw_line) - len(raw_line.lstrip(" "))
        indent = " " * indent_len
        cleaned = _rewrite_parts(raw_line).strip()

        if not cleaned:
            out_lines.append("")
            i += 1
            continue

        # Preserve # comments untouched
        if cleaned.startswith("#"):
            out_lines.append(indent + cleaned)
            i += 1
            continue

        # 1. Durable Immutable Record Block:
        # durable record PacketName:
        #     field: String
        m_rec = re.match(r"^durable\s+record\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*$", cleaned)
        if m_rec:
            rec_name = m_rec.group(1)
            out_lines.append(f"{indent}@_dc.dataclass(frozen=True)")
            out_lines.append(f"{indent}class {rec_name}(DurableRecord):")
            i += 1
            field_count = 0
            while i < n:
                sub_raw = lines[i]
                sub_stripped = _rewrite_parts(sub_raw).strip()
                if not sub_stripped:
                    i += 1
                    continue
                sub_indent = len(sub_raw) - len(sub_raw.lstrip(" "))
                if sub_indent <= indent_len:
                    break
                m_field = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([a-zA-Z_][a-zA-Z0-9_]*)(?:\s*=\s*(.+))?$", sub_stripped)
                if m_field:
                    f_name, f_type, f_def = m_field.group(1), m_field.group(2), m_field.group(3)
                    py_type = HAVEN_TYPE_MAP.get(f_type, f_type)
                    if f_def:
                        out_lines.append(f"{' ' * sub_indent}{f_name}: {py_type} = {f_def}")
                    else:
                        out_lines.append(f"{' ' * sub_indent}{f_name}: {py_type}")
                    field_count += 1
                else:
                    out_lines.append(f"{' ' * sub_indent}{sub_stripped}")
                i += 1
            if field_count == 0:
                out_lines.append(f"{indent}    pass")
            continue

        # 2. Import shims for built-in Haven/ODCS virtual modules
        if re.match(r"^(?:from\s+(?:odcs|haven_ai|crypto)(?:\.[a-zA-Z0-9_]+)?\s+import|import\s+(?:crypto|odcs))\b", cleaned):
            out_lines.append(f"{indent}# [haven-builtin] {cleaned}")
            i += 1
            continue

        # 3. Natural English Function Definitions
        m_fn = re.match(r"^(?:define|to|task|function)\s+([a-zA-Z_][a-zA-Z0-9_]*\s*\(.*\))\s*:\s*$", cleaned)
        if m_fn:
            out_lines.append(f"{indent}def {m_fn.group(1)}:")
            i += 1
            continue

        # 4. Natural English Control Flow
        if re.match(r"^repeat\s+(.+)\s+times\s*:\s*$", cleaned):
            count_expr = re.match(r"^repeat\s+(.+)\s+times\s*:\s*$", cleaned).group(1)
            out_lines.append(f"{indent}for iteration in range(1, int({count_expr}) + 1):")
            i += 1
            continue

        m_each = re.match(r"^for\s+each\s+(.+?)\s+in\s+(.+)\s*:\s*$", cleaned)
        if m_each:
            out_lines.append(f"{indent}for {m_each.group(1)} in {m_each.group(2)}:")
            i += 1
            continue

        m_unless = re.match(r"^unless\s+(.+)\s*:\s*$", cleaned)
        if m_unless:
            out_lines.append(f"{indent}if not ({m_unless.group(1)}):")
            i += 1
            continue

        m_until = re.match(r"^until\s+(.+)\s*:\s*$", cleaned)
        if m_until:
            out_lines.append(f"{indent}while not ({m_until.group(1)}):")
            i += 1
            continue

        if re.match(r"^forever\s*:\s*$", cleaned):
            out_lines.append(f"{indent}while True:")
            i += 1
            continue

        m_ensure = re.match(r"^ensure\s+(.+?)(?:\s+(?:otherwise|because)\s+(.+))?$", cleaned)
        if m_ensure:
            cond_expr = _fold_pipeline(m_ensure.group(1).strip())
            msg_expr = m_ensure.group(2).strip() if m_ensure.group(2) else None
            out_lines.append(f"{indent}assert {cond_expr}, {msg_expr}" if msg_expr else f"{indent}assert {cond_expr}")
            i += 1
            continue

        m_elif = re.match(r"^(?:otherwise\s+if|or\s+whenever)\s+(.+)\s*:\s*$", cleaned)
        if m_elif:
            out_lines.append(f"{indent}elif {m_elif.group(1)}:")
            i += 1
            continue

        m_if = re.match(r"^(?:whenever|when)\s+(.+)\s*:\s*$", cleaned)
        if m_if:
            out_lines.append(f"{indent}if {m_if.group(1)}:")
            i += 1
            continue

        if re.match(r"^otherwise\s*:\s*$", cleaned):
            out_lines.append(f"{indent}else:")
            i += 1
            continue

        # 5. Error handling (`on error as e:` / `recover:` / `except SomeError as e:`)
        m_err_as = re.match(r"^(?:on\s+error|recover)\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*$", cleaned)
        if m_err_as:
            out_lines.append(f"{indent}except Exception as {m_err_as.group(1)}:")
            i += 1
            continue

        if re.match(r"^(?:on\s+error|recover)\s*:\s*$", cleaned):
            out_lines.append(f"{indent}except Exception:")
            i += 1
            continue

        # 6. Natural English Assignments & Mutations
        m_set = re.match(r"^(?:set\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+to|let\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:be|=)|remember\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+as)\s+(.+)$", cleaned)
        if m_set:
            var_name = m_set.group(1) or m_set.group(2) or m_set.group(3)
            rhs = _fold_pipeline(m_set.group(4))
            out_lines.append(f"{indent}{var_name} = {rhs}")
            i += 1
            continue

        m_inc = re.match(r"^increase\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+by\s+(.+)$", cleaned)
        if m_inc:
            out_lines.append(f"{indent}{m_inc.group(1)} += {_fold_pipeline(m_inc.group(2))}")
            i += 1
            continue

        m_dec = re.match(r"^decrease\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+by\s+(.+)$", cleaned)
        if m_dec:
            out_lines.append(f"{indent}{m_dec.group(1)} -= {_fold_pipeline(m_dec.group(2))}")
            i += 1
            continue

        # 7. Return / Give Back
        m_ret = re.match(r"^give\s+back(?:\s+(.+))?$", cleaned)
        if m_ret:
            expr = m_ret.group(1)
            if expr:
                out_lines.append(f"{indent}return {_fold_pipeline(expr)}")
            else:
                out_lines.append(f"{indent}return")
            i += 1
            continue

        # 8. ODCS Native Intent Preservation:
        # preserve intent "ActionName" with {"k": "v"} as receipt
        m_intent = re.match(
            r"^preserve\s+intent\s+(.+?)(?:\s+with\s+(.+?))?(?:\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*))?$",
            cleaned,
        )
        if m_intent:
            act_expr = m_intent.group(1).strip()
            pay_expr = m_intent.group(2).strip() if m_intent.group(2) else "{}"
            target_var = m_intent.group(3) or "_last_receipt"
            out_lines.append(f"{indent}{target_var} = ZeroIntentLoss.preserve({act_expr}, {pay_expr})")
            i += 1
            continue

        # 9. Natural Print / Say / Show statements
        m_say = re.match(r"^(?:say|show|print)\s+(.+)$", cleaned)
        if m_say and not cleaned.startswith("print("):
            inner = m_say.group(1).strip()
            # Keep `print("x")` un-double-wrapped if user wrote `say ("hi")`? No, print((...)) is valid, or clean parens
            out_lines.append(f"{indent}print({_fold_pipeline(inner)})")
            i += 1
            continue

        # 10. Default expression / pipeline folding
        out_lines.append(f"{indent}{_fold_pipeline(cleaned)}")
        i += 1

    body = _convert_call_named_colons("\n".join(out_lines))
    if include_prelude:
        return HAVEN_PRELUDE.lstrip() + "\n# --- Transpiled Haven User Program ---\n" + body + "\n"
    return body + "\n"


def execute_haven_file(path: str, show_compiled: bool = False) -> int:
    """Load, transpile, validate, and run a `.hvn` file."""
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    compiled = transpile_haven(src, include_prelude=True)
    if show_compiled:
        print("=== COMPILED PYTHON TARGET ===")
        print(transpile_haven(src, include_prelude=False))
        print("=== EXECUTION OUTPUT ===")
    try:
        ast.parse(compiled)
    except SyntaxError as exc:
        print(f"[Haven SyntaxError] line {exc.lineno}: {exc.msg}", file=sys.stderr)
        return 1
    ns: Dict[str, Any] = {"__name__": "__main__", "__file__": os.path.abspath(path)}
    exec(compile(compiled, path, "exec"), ns)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Haven Language v2.0 Natural-English Toolchain & VM")
    sub = parser.add_subparsers(dest="cmd")

    p_run = sub.add_parser("run", help="Run a .hvn script")
    p_run.add_argument("file", help="Path to .hvn file")
    p_run.add_argument("--show-compiled", action="store_true", help="Print compiled Python before running")

    p_comp = sub.add_parser("compile", help="Transpile a .hvn script to Python")
    p_comp.add_argument("file", help="Path to .hvn file")

    p_lint = sub.add_parser("lint", help="Validate Haven syntax without executing")
    p_lint.add_argument("file", help="Path to .hvn file")

    sub.add_parser("repl", help="Launch interactive Haven REPL")

    args, unknown = parser.parse_known_args()
    if args.cmd == "run":
        sys.argv = [args.file] + unknown
        return execute_haven_file(args.file, show_compiled=args.show_compiled)
    if args.cmd == "compile":
        with open(args.file, "r", encoding="utf-8") as fh:
            print(transpile_haven(fh.read(), include_prelude=False))
        return 0
    if args.cmd == "lint":
        with open(args.file, "r", encoding="utf-8") as fh:
            compiled = transpile_haven(fh.read(), include_prelude=True)
        ast.parse(compiled)
        print(f"[OK] {args.file} passed Haven v2.0 AST verification.")
        return 0
    if args.cmd == "repl":
        print("Haven Language v2.0 Interactive REPL (type 'exit' to quit)")
        ns: Dict[str, Any] = {}
        exec(compile(HAVEN_PRELUDE, "<haven-prelude>", "exec"), ns)
        while True:
            try:
                line = input("haven> ")
            except EOFError:
                break
            if line.strip() in ("exit", "quit"):
                break
            if not line.strip():
                continue
            try:
                py = transpile_haven(line, include_prelude=False)
                exec(compile(py, "<repl>", "exec"), ns)
            except Exception as exc:
                print(f"[Haven Error] {exc}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
