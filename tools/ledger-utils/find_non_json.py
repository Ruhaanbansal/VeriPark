import json
from pathlib import Path

p = Path("data/ledger/ledger.jsonl")
raw_lines = p.read_text(encoding="utf-8").splitlines()
print(f"Total lines: {len(raw_lines)}")

for i, l in enumerate(raw_lines):
    try:
        json.loads(l)
    except Exception as e:
        print(f"Line {i} failed to parse: {e} | repr: {repr(l[:80])}")
