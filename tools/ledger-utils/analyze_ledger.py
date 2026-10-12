import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path("backend/src").resolve()))
from veripark.vericore.ledger import compute_block_hash, compute_evidence_hash, GENESIS_HASH

p = Path("data/ledger/ledger.jsonl")
lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"Total lines: {len(lines)}")

prev = GENESIS_HASH
issues = []
for i, l in enumerate(lines):
    b = json.loads(l)
    p_hash = b.get("previous_hash")
    b_hash = b.get("block_hash")
    e_hash = b.get("evidence_hash")
    rec_price = b.get("recorded_price")
    
    calc_ev = compute_evidence_hash(b.get("evidence_payload", {}))
    calc_b = compute_block_hash(p_hash, b.get("decision_id"), b.get("timestamp"), rec_price, e_hash)
    
    if p_hash != prev:
        issues.append(f"Block {i}: prev_hash={p_hash[:10]} != expected={prev[:10]}")
    if calc_ev != e_hash:
        issues.append(f"Block {i}: evidence hash mismatch")
    if calc_b != b_hash:
        issues.append(f"Block {i}: block hash mismatch")
        
    prev = b_hash

print(f"Total issues found: {len(issues)}")
for iss in issues[:10]:
    print(" ", iss)
