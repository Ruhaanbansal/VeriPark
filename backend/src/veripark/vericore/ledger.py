"""Component 4: Verifiable Decision-Evidence Ledger.

Maintains an append-only, SHA-256 hash-chained audit ledger of every decision,
its evidence snapshot, claim materiality, verification tiers, and resummation outcome.

Schema versioning:
- Legacy (v1/unversioned): block_hash covers (previous_hash, decision_id, timestamp, recorded_price, evidence_hash).
- Schema v2: block_hash covers (previous_hash, decision_id, timestamp, lot_id, proposed_price, recorded_price, delta, was_adjusted, evidence_hash).
- Truncation detection via sidecar head file (.head) tracking last block hash and count.
- Thread-safe appends via single-line flush.
- Stats/queries deduplicate by decision_id (last-wins) without rewriting history.
"""

import json
import hashlib
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

_ROOT_LEDGER = Path(__file__).resolve().parents[4] / "data" / "ledger" / "ledger.jsonl"
_BACKEND_LEDGER = Path(__file__).resolve().parents[3] / "data" / "ledger" / "ledger.jsonl"
DEFAULT_LEDGER_PATH = _ROOT_LEDGER if _ROOT_LEDGER.exists() else _BACKEND_LEDGER
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
    """Computes legacy v1 cryptographic block hash chaining to previous block."""
    raw = f"{previous_hash}|{decision_id}|{timestamp}|{recorded_price:.2f}|{evidence_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def compute_block_hash_v2(
    previous_hash: str,
    decision_id: str,
    timestamp: str,
    lot_id: str,
    proposed_price: float,
    recorded_price: float,
    delta: float,
    was_adjusted: bool,
    evidence_hash: str
) -> str:
    """Computes v2 cryptographic block hash covering all top-level decision fields."""
    raw = f"{previous_hash}|{decision_id}|{timestamp}|{lot_id}|{proposed_price:.2f}|{recorded_price:.2f}|{delta:.2f}|{bool(was_adjusted)}|{evidence_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class DecisionLedger:
    def __init__(self, file_path: Path | str | None = None):
        self.path = Path(file_path) if file_path else DEFAULT_LEDGER_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()
        self.head_path = self.path.parent / f"{self.path.stem}.head"
        self._lock = threading.Lock()

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

    def get_block_count(self) -> int:
        """Returns the number of non-empty records in the ledger file."""
        if not self.path.exists():
            return 0
        count = 0
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    def _write_head(self, last_block_hash: str, block_count: int) -> None:
        """Updates the sidecar head file atomically tracking the chain tail."""
        head_data = {
            "last_block_hash": last_block_hash,
            "block_count": block_count,
            "count": block_count,
            "head_hash": last_block_hash
        }
        with open(self.head_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(head_data, indent=2) + "\n")
            f.flush()

    def record_decision(
        self,
        decision_id: str,
        lot_id: str,
        pricing_result: Dict[str, Any],
        resummation_result: Dict[str, Any],
        claim_verdicts: List[Dict[str, Any]],
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Appends a new verified decision record (Schema v2) to the tamper-evident ledger.
        
        Guarded with thread locking and atomic line flush.
        Idempotent per decision_id.
        """
        with self._lock:
            existing = self.get_record(decision_id)
            if existing:
                return existing

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
            proposed_price = float(resummation_result.get("proposed_price", 0.0))
            delta = float(resummation_result.get("delta", 0.0))
            was_adjusted = bool(resummation_result.get("was_adjusted", False))

            # Schema v2 block hash covers all top-level decision fields
            block_hash = compute_block_hash_v2(
                previous_hash=previous_hash,
                decision_id=decision_id,
                timestamp=timestamp,
                lot_id=lot_id,
                proposed_price=proposed_price,
                recorded_price=recorded_price,
                delta=delta,
                was_adjusted=was_adjusted,
                evidence_hash=evidence_hash
            )

            entry = {
                "schema_version": 2,
                "decision_id": decision_id,
                "timestamp": timestamp,
                "lot_id": lot_id,
                "recorded_price": recorded_price,
                "proposed_price": proposed_price,
                "delta": delta,
                "was_adjusted": was_adjusted,
                "evidence_hash": evidence_hash,
                "previous_hash": previous_hash,
                "block_hash": block_hash,
                "sealed": True,
                "evidence_payload": evidence_payload
            }

            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()

            new_count = self.get_block_count()
            self._write_head(block_hash, new_count)

            return entry

    def get_record(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific decision record from the ledger (last-wins deduplication)."""
        if not self.path.exists():
            return None
        matching = None
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        rec = json.loads(line)
                        if rec.get("decision_id") == decision_id:
                            matching = rec
                    except Exception:
                        continue
        return matching

    def get_all_records(self, deduplicate: bool = False) -> List[Dict[str, Any]]:
        """Fetch all ledger records, optionally deduplicated by decision_id (last-wins)."""
        if not self.path.exists():
            return []
        records = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        continue
        if not deduplicate:
            return records

        deduped: Dict[str, Dict[str, Any]] = {}
        for rec in records:
            did = rec.get("decision_id")
            if did:
                deduped[did] = rec
            else:
                deduped[f"anon-{id(rec)}"] = rec
        return list(deduped.values())

    def verify_chain(self) -> Tuple[bool, str]:
        """Validates the cryptographic integrity of the entire ledger chain.
        
        Backward compatible with legacy v1 blocks (no schema_version) and schema_version=2.
        Detects tail truncation when sidecar head file exists.
        
        Returns (is_valid: bool, details: str)
        """
        if not self.path.exists() or self.path.stat().st_size == 0:
            return True, "Ledger is empty, chain intact."

        expected_prev_hash = GENESIS_HASH
        block_count = 0
        last_block_hash = GENESIS_HASH

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

                # 3. Verify block hash recalculation (schema_version aware)
                schema_version = entry.get("schema_version", 1)
                if schema_version == 2:
                    expected_block_hash = compute_block_hash_v2(
                        previous_hash=entry.get("previous_hash", ""),
                        decision_id=entry.get("decision_id", ""),
                        timestamp=entry.get("timestamp", ""),
                        lot_id=entry.get("lot_id", ""),
                        proposed_price=float(entry.get("proposed_price", 0.0)),
                        recorded_price=float(entry.get("recorded_price", 0.0)),
                        delta=float(entry.get("delta", 0.0)),
                        was_adjusted=bool(entry.get("was_adjusted", False)),
                        evidence_hash=entry.get("evidence_hash", "")
                    )
                else:
                    expected_block_hash = compute_block_hash(
                        entry.get("previous_hash", ""),
                        entry.get("decision_id", ""),
                        entry.get("timestamp", ""),
                        float(entry.get("recorded_price", 0.0)),
                        entry.get("evidence_hash", "")
                    )

                if expected_block_hash != entry.get("block_hash"):
                    return False, f"Tampered block hash at block {line_idx}: block_hash mismatch"

                expected_prev_hash = entry.get("block_hash")
                last_block_hash = entry.get("block_hash")

        # 4. Verify truncation against sidecar head file if present
        if self.head_path.exists():
            try:
                head_content = json.loads(self.head_path.read_text(encoding="utf-8"))
                expected_count = head_content.get("block_count", head_content.get("count", 0))
                expected_head_hash = head_content.get("last_block_hash", head_content.get("head_hash", ""))
                if block_count != expected_count or last_block_hash != expected_head_hash:
                    return False, f"head mismatch: sidecar expected {expected_count} blocks with head {expected_head_hash}, found {block_count} blocks with head {last_block_hash}"
            except Exception as e:
                return False, f"head mismatch: could not read sidecar head file: {e}"

        return True, f"Verified {block_count} cryptographically-chained blocks successfully."
