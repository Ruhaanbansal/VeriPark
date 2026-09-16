"""Component 4: Verifiable Decision-Evidence Ledger.

Maintains an append-only, SHA-256 hash-chained audit ledger of every decision,
its evidence snapshot, claim materiality, verification tiers, and clamping outcome.
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

DEFAULT_LEDGER_PATH = Path(__file__).resolve().parents[3] / "data" / "ledger" / "ledger.jsonl"
GENESIS_HASH = "0" * 64

def compute_evidence_hash(evidence_payload: Dict[str, Any]) -> str:
    """Computes deterministic SHA-256 hash of evidence and factor breakdown."""
    serialized = json.dumps(evidence_payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def compute_block_hash(
    previous_hash: str,
    decision_id: str,
    timestamp: str,
    recorded_price: float,
    evidence_hash: str
) -> str:
    """Computes cryptographic block hash chaining to previous block."""
    raw = f"{previous_hash}|{decision_id}|{timestamp}|{recorded_price:.2f}|{evidence_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class DecisionLedger:
    def __init__(self, file_path: Path | str | None = None):
        self.path = Path(file_path) if file_path else DEFAULT_LEDGER_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def get_last_block_hash(self) -> str:
        """Reads the hash of the most recent block, or returns GENESIS_HASH."""
        if not self.path.exists() or self.path.stat().st_size == 0:
            return GENESIS_HASH
        
        last_line = ""
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line
        
        if not last_line:
            return GENESIS_HASH
        try:
            record = json.loads(last_line)
            return record.get("block_hash", GENESIS_HASH)
        except Exception:
            return GENESIS_HASH

    def record_decision(
        self,
        decision_id: str,
        lot_id: str,
        pricing_result: Dict[str, Any],
        resummation_result: Dict[str, Any],
        claim_verdicts: List[Dict[str, Any]],
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Appends a new verified decision record to the tamper-evident ledger."""
        if not timestamp:
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        evidence_payload = {
            "lot_id": lot_id,
            "base_price": pricing_result.get("base_price"),
            "proposed_price": pricing_result.get("proposed_price"),
            "factors": pricing_result.get("factors"),
            "verdicts": claim_verdicts,
            "resummation": resummation_result
        }

        evidence_hash = compute_evidence_hash(evidence_payload)
        previous_hash = self.get_last_block_hash()
        recorded_price = float(resummation_result.get("final_price", 0.0))
        block_hash = compute_block_hash(
            previous_hash,
            decision_id,
            timestamp,
            recorded_price,
            evidence_hash
        )

        entry = {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "lot_id": lot_id,
            "recorded_price": recorded_price,
            "proposed_price": float(resummation_result.get("proposed_price", 0.0)),
            "delta": float(resummation_result.get("delta", 0.0)),
            "was_adjusted": bool(resummation_result.get("was_adjusted", False)),
            "evidence_hash": evidence_hash,
            "previous_hash": previous_hash,
            "block_hash": block_hash,
            "sealed": True,
            "evidence_payload": evidence_payload
        }

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def get_record(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific decision record from the ledger."""
        if not self.path.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    if rec.get("decision_id") == decision_id:
                        return rec
        return None

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Fetch all ledger records."""
        if not self.path.exists():
            return []
        records = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def verify_chain(self) -> Tuple[bool, str]:
        """Validates the cryptographic integrity of the entire ledger chain.
        
        Returns (is_valid: bool, details: str)
        """
        if not self.path.exists() or self.path.stat().st_size == 0:
            return True, "Ledger is empty, chain intact."

        expected_prev_hash = GENESIS_HASH
        block_count = 0

        with open(self.path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                if not line.strip():
                    continue
                block_count += 1
                try:
                    entry = json.loads(line)
                except Exception as e:
                    return False, f"JSON parse failure at block {line_idx}: {e}"

                # 1. Verify previous hash chaining
                prev_h = entry.get("previous_hash")
                if prev_h != expected_prev_hash:
                    return False, f"Broken link at block {line_idx}: previous_hash {prev_h} != expected {expected_prev_hash}"

                # 2. Verify evidence hash recalculation
                ev_payload = entry.get("evidence_payload", {})
                expected_ev_hash = compute_evidence_hash(ev_payload)
                if expected_ev_hash != entry.get("evidence_hash"):
                    return False, f"Tampered evidence at block {line_idx}: evidence_hash mismatch"

                # 3. Verify block hash recalculation
                expected_block_hash = compute_block_hash(
                    entry["previous_hash"],
                    entry["decision_id"],
                    entry["timestamp"],
                    entry["recorded_price"],
                    entry["evidence_hash"]
                )
                if expected_block_hash != entry.get("block_hash"):
                    return False, f"Tampered block hash at block {line_idx}: block_hash mismatch"

                expected_prev_hash = entry.get("block_hash")

        return True, f"Verified {block_count} cryptographically-chained blocks successfully."
