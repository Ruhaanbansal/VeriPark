import json
from pathlib import Path

p = Path("data/ledger/ledger.jsonl")
lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"Line 131: {lines[131]}")
print(f"Line 132: {lines[132]}")
print(f"Exact match: {lines[131] == lines[132]}")
