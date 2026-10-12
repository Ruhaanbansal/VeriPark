import sys
import json
from pathlib import Path

# Add backend/src to sys.path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from veripark.vericore.ledger import DecisionLedger

ledger = DecisionLedger()
valid, msg = ledger.verify_chain()
print("Valid:", valid)
print("Message:", msg)

# Let's inspect block 131, 132, 133
ledger_file = ledger.path
lines = [l for l in ledger_file.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"Total lines in ledger: {len(lines)}")
if len(lines) >= 132:
    for idx in range(max(0, 130), min(len(lines), 136)):
        b = json.loads(lines[idx])
        print(f"Index {idx}: decision_id={b.get('decision_id')} prev={b.get('previous_hash')[:12]} curr={b.get('block_hash')[:12]}")
