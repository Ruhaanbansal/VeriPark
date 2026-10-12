import sys
import json
from pathlib import Path

# Add backend/src to sys.path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from veripark.vericore.ledger import DecisionLedger

root_ledger_path = Path("data/ledger/ledger.jsonl")
ledger = DecisionLedger(file_path=root_ledger_path)
valid, msg = ledger.verify_chain()
print("Valid:", valid)
print("Message:", msg)

lines = [l for l in root_ledger_path.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"Total lines in root ledger: {len(lines)}")
if len(lines) >= 132:
    for idx in range(max(0, 130), min(len(lines), 136)):
        b = json.loads(lines[idx])
        print(f"Index {idx}: decision_id={b.get('decision_id')} prev={b.get('previous_hash')[:16]} curr={b.get('block_hash')[:16]}")
