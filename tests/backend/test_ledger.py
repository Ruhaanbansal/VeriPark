import json
import pytest
from pathlib import Path
from veripark.vericore.ledger import DecisionLedger

def test_ledger_append_and_chain_verification(tmp_path: Path):
    ledger_file = tmp_path / "test_ledger.jsonl"
    ledger = DecisionLedger(file_path=ledger_file)

    # Empty chain is valid
    is_valid, msg = ledger.verify_chain()
    assert is_valid is True

    # Record first decision
    p1 = {"base_price": 100.0, "proposed_price": 150.0, "factors": []}
    r1 = {"final_price": 150.0, "proposed_price": 150.0, "delta": 0.0, "was_adjusted": False}
    ledger.record_decision("dec-001", "lot-1", p1, r1, [], "2026-09-16T12:00:00Z")

    # Record second decision
    p2 = {"base_price": 80.0, "proposed_price": 120.0, "factors": []}
    r2 = {"final_price": 100.0, "proposed_price": 120.0, "delta": 20.0, "was_adjusted": True}
    ledger.record_decision("dec-002", "lot-2", p2, r2, [], "2026-09-16T12:05:00Z")

    # Verify untampered chain
    is_valid, msg = ledger.verify_chain()
    assert is_valid is True
    assert "Verified 2 cryptographically-chained blocks" in msg

def test_ledger_tamper_detection(tmp_path: Path):
    ledger_file = tmp_path / "tamper_ledger.jsonl"
    ledger = DecisionLedger(file_path=ledger_file)

    # Add 2 blocks
    p1 = {"base_price": 50.0, "proposed_price": 80.0, "factors": []}
    r1 = {"final_price": 80.0, "proposed_price": 80.0, "delta": 0.0, "was_adjusted": False}
    ledger.record_decision("dec-1", "lot-1", p1, r1, [], "2026-09-16T10:00:00Z")

    p2 = {"base_price": 60.0, "proposed_price": 90.0, "factors": []}
    r2 = {"final_price": 90.0, "proposed_price": 90.0, "delta": 0.0, "was_adjusted": False}
    ledger.record_decision("dec-2", "lot-2", p2, r2, [], "2026-09-16T10:01:00Z")

    assert ledger.verify_chain()[0] is True

    # Tamper with the first block: modify recorded_price illegally
    lines = ledger_file.read_text(encoding="utf-8").strip().split("\n")
    block1 = json.loads(lines[0])
    block1["recorded_price"] = 999.0  # Illegal price alteration
    lines[0] = json.dumps(block1)
    ledger_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Chain verification MUST fail
    is_valid, reason = ledger.verify_chain()
    assert is_valid is False
    assert "Tampered" in reason or "Broken link" in reason
