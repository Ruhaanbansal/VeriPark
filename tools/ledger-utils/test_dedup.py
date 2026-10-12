import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path("backend/src").resolve()))
from veripark.vericore.ledger import DecisionLedger

p = Path("data/ledger/ledger.jsonl")
lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"Original lines: {len(lines)}")

# Check any consecutive identical lines or other breaks
deduped = []
for i, line in enumerate(lines):
    if i > 0 and line == lines[i-1]:
        print(f"Skipping duplicate line at index {i}")
        continue
    deduped.append(line)

print(f"Deduped lines: {len(deduped)}")

# Write to a temp file and test verify_chain
tmp_p = Path("data/ledger/ledger_test.jsonl")
tmp_p.write_text("\n".join(deduped) + "\n", encoding="utf-8")

ledger = DecisionLedger(file_path=tmp_p)
valid, msg = ledger.verify_chain()
print("Test ledger valid:", valid)
print("Test ledger msg:", msg)
