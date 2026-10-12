import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path("backend/src").resolve()))
from veripark.vericore.ledger import compute_block_hash, compute_evidence_hash, GENESIS_HASH

p = Path("data/ledger/ledger.jsonl")
lines = p.read_text(encoding="utf-8").splitlines()
print(f"Raw lines: {len(lines)}")

valid_blocks = []
for i, l in enumerate(lines):
    raw = l.strip()
    if not raw:
        continue
    try:
        b = json.loads(raw)
        valid_blocks.append((i, b))
    except Exception as e:
        print(f"Corrupt/empty line {i}: {e} content: {raw[:50]}")

print(f"Valid parsed blocks: {len(valid_blocks)}")

prev = GENESIS_HASH
issues = []
for line_idx, b in valid_blocks:
    p_hash = b.get("previous_hash")
    b_hash = b.get("block_hash")
    e_hash = b.get("evidence_hash")
    rec_price = b.get("recorded_price")
    
    calc_ev = compute_evidence_hash(b.get("evidence_payload", {}))
    calc_b = compute_block_hash(p_hash, b.get("decision_id"), b.get("timestamp"), rec_price, e_hash)
    
    if p_hash != prev:
        issues.append((line_idx, f"prev_hash mismatch: got {p_hash[:10]} expected {prev[:10]}"))
    if calc_ev != e_hash:
        issues.append((line_idx, "evidence hash mismatch"))
    if calc_b != b_hash:
        issues.append((line_idx, "block hash mismatch"))
        
    prev = b_hash

print(f"Total issues: {len(issues)}")
for line_idx, msg in issues[:20]:
    print(f"  Line {line_idx}: {msg}")
