# Ledger Utilities

Developer/diagnostic scripts for inspecting and maintaining the VeriCore append-only ledger.

> **⚠️ Do not use in production.** These are offline analysis tools only.

| Script | Purpose |
|---|---|
| `analyze_ledger.py` | Summarise ledger statistics (block count, tier breakdown) |
| `analyze_ledger_robust.py` | Fault-tolerant ledger analysis (skips malformed lines) |
| `inspect_ledger.py` | Pretty-print individual ledger records |
| `inspect_root_ledger.py` | Inspect the canonical `data/ledger/ledger.jsonl` |
| `reseal_ledger.py` | Re-compute and write `.head` sidecar after manual edits |
| `find_non_json.py` | Scan ledger file for malformed (non-JSON) lines |
| `check_dup.py` | Detect duplicate `block_hash` entries in the ledger |
| `test_committed.py` | Verify integrity of `committed_ledger.jsonl` snapshot |
| `test_dedup.py` | Regression test for de-duplication logic |
| `test_fix_ledger.py` | Regression test covering ledger repair scenarios |

## Usage

Run from the project root:

```bash
python tools/ledger-utils/inspect_ledger.py
python tools/ledger-utils/analyze_ledger_robust.py
```
