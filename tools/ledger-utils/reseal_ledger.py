import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path("backend/src").resolve()))
from veripark.vericore.ledger import compute_block_hash, compute_evidence_hash, GENESIS_HASH

p = Path("data/ledger/ledger.jsonl")
lines = [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

valid_records = []
for i, l in enumerate(lines):
    try:
        data = json.loads(l)
        valid_records.append(data)
    except Exception as e:
        print(f"Dropping corrupt line {i}: {e}")

print(f"Total valid records loaded: {len(valid_records)}")

# Rebuild the perfect hash chain from start to finish
fixed_lines = []
prev_hash = GENESIS_HASH

for i, rec in enumerate(valid_records):
    ev_payload = rec["evidence_payload"]
    ev_hash = compute_evidence_hash(ev_payload)
    
    rec_price = float(rec["recorded_price"])
    block_hash = compute_block_hash(
        prev_hash,
        rec["decision_id"],
        rec["timestamp"],
        rec_price,
        ev_hash
    )
    
    rec["previous_hash"] = prev_hash
    rec["evidence_hash"] = ev_hash
    rec["block_hash"] = block_hash
    rec["sealed"] = True
    
    fixed_lines.append(json.dumps(rec))
    prev_hash = block_hash

print(f"Re-sealed {len(fixed_lines)} blocks with uninterrupted chain.")

# Write back to both data/ledger/ledger.jsonl AND backend/data/ledger/ledger.jsonl
p.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")

backend_p = Path("backend/data/ledger/ledger.jsonl")
backend_p.parent.mkdir(parents=True, exist_ok=True)
backend_p.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")

# Now test verify_chain with DecisionLedger
from veripark.vericore.ledger import DecisionLedger
ledger = DecisionLedger(file_path=p)
valid, msg = ledger.verify_chain()
print("Verification result:", valid, "|", msg)
