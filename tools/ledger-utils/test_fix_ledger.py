import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path("backend/src").resolve()))
from veripark.vericore.ledger import compute_block_hash, compute_evidence_hash, GENESIS_HASH

p = Path("data/ledger/ledger.jsonl")
lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"Total lines: {len(lines)}")

# Look at 131, 132, 133
b131 = json.loads(lines[131])
b132 = json.loads(lines[132])
b133 = json.loads(lines[133])

print("131 prev:", b131["previous_hash"])
print("131 curr:", b131["block_hash"])
print("132 prev:", b132["previous_hash"])
print("132 curr:", b132["block_hash"])
print("133 prev:", b133["previous_hash"])
print("133 curr:", b133["block_hash"])

print("b131 == b132:", b131 == b132)
print("b133 prev == b131 curr:", b133["previous_hash"] == b131["block_hash"])

# What if we delete index 132 from lines?
lines_no_132 = lines[:132] + lines[133:]
print("Length without 132:", len(lines_no_132))

prev = GENESIS_HASH
issues = []
for i, l in enumerate(lines_no_132):
    b = json.loads(l)
    p_hash = b.get("previous_hash")
    b_hash = b.get("block_hash")
    e_hash = b.get("evidence_hash")
    rec_price = b.get("recorded_price")
    
    calc_ev = compute_evidence_hash(b.get("evidence_payload", {}))
    calc_b = compute_block_hash(p_hash, b.get("decision_id"), b.get("timestamp"), rec_price, e_hash)
    
    if p_hash != prev:
        issues.append(f"Block {i} (orig ~{i if i < 132 else i+1}): prev={p_hash[:8]} expected={prev[:8]}")
    if calc_ev != e_hash:
        issues.append(f"Block {i}: evidence hash mismatch")
    if calc_b != b_hash:
        issues.append(f"Block {i}: block hash mismatch")
    prev = b_hash

print(f"Issues without line 132: {len(issues)}")
for iss in issues[:10]:
    print(" ", iss)
