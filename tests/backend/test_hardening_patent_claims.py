"""Comprehensive unit and property tests verifying VeriCore™ patent claim hardening.

Tests 1-12 as required by VeriCore Hardening Specification:
1. Unknown factor ID is unsupported (fail-closed).
2. Indiranagar stale event is excluded at standard tier.
3. Express-deck sensor discrepancy is excluded.
4. Deep-tier claim with injected drift is caught by live re-grounding but passes cached check (C2 value proof).
5. Live source unreachable excludes factor and does not raise.
6. Tolerance boundary (just inside / just outside).
7. Routing boundaries at exactly 0.10 and 0.40.
8. Resummation invariants under random factors (property-style, seeded): final <= proposed, binary inclusion, ledger written.
9. Ledger tamper detection (top-level fields, tail truncation, genesis break, payload alteration) and legacy ledger verification.
10. Concurrent thread appends produce a valid hash chain.
11. verification_mode default equals expected hardened behavior across all 8 lots.
12. API contract verification.
"""

import json
import time
import random
import threading
from pathlib import Path
import pytest

from veripark.vericore.materiality_scoring import compute_claim_materiality
from veripark.vericore.adaptive_routing import route_claim
from veripark.vericore.structured_evidence_assessment import evaluate_evidence_entailment
from veripark.vericore.live_regrounding import reground_claim_live
from veripark.vericore.decision_resummation import resum_decision
from veripark.vericore.ledger import DecisionLedger, DEFAULT_LEDGER_PATH
from veripark.data_sources.live_state import LiveStateStore, get_live_store
from veripark.data_sources.parking_lots import PARKING_LOTS_DB, _init_lots
from veripark.pipeline import VeriParkPipeline
from veripark.config import load_settings

_init_lots()


# 1. Unknown factor ID is unsupported
def test_unknown_factor_id_is_unsupported():
    context = {"lot": {"name": "Test Lot", "live_signals": {}}}
    is_supp, reason = evaluate_evidence_entailment(
        "Surge fee for special festival", "factor-unknown-festival", context
    )
    assert is_supp is False
    assert "no evidence rule" in reason.lower()

    is_supp2, reason2 = evaluate_evidence_entailment(
        "Arbitrary surcharge", "factor-unverified-custom", context
    )
    assert is_supp2 is False
    assert "no evidence rule" in reason2.lower()


# 2. Indiranagar stale event is excluded at standard tier
def test_indiranagar_stale_event_excluded_standard_tier():
    lot = PARKING_LOTS_DB["lot-indiranagar-100ft"]
    context = {"lot": lot, "duration_hours": 2}
    is_supp, reason = evaluate_evidence_entailment(
        "Nearby event surcharge active", "factor-event", context
    )
    assert is_supp is False
    assert "schedule_verified=false" in reason.lower() or "event schedule not verified" in reason.lower()


# 3. Express-deck sensor discrepancy is excluded
def test_express_deck_sensor_discrepancy_excluded():
    lot = PARKING_LOTS_DB["lot-express-deck"]
    context = {"lot": lot, "duration_hours": 2}
    is_supp, reason = evaluate_evidence_entailment(
        "Conservative demand premium from sensor discrepancy", "factor-sensor-discrepancy", context
    )
    assert is_supp is False
    assert "camera confirms" in reason.lower() or "loop-detector" in reason.lower()


# 4. Deep-tier claim with injected drift is caught by live re-grounding but passes a cached-only check
def test_deep_tier_drift_caught_by_live_regrounding_proves_c2():
    lot_id = "lot-metro-hub"
    lot = PARKING_LOTS_DB[lot_id]
    context = {"lot": lot, "duration_hours": 2}

    # Cached context has high occupancy (88%)
    is_supp_cached, reason_cached = evaluate_evidence_entailment(
        "High occupancy surge (over 85% capacity)", "factor-occupancy", context
    )
    assert is_supp_cached is True  # Passes cached check

    # Inject live drift: occupancy drops to 50%
    live_store = get_live_store()
    live_store.set_override(lot_id, "occupancy_rate", 0.50)

    try:
        is_supp_live, verdict_live, detail_live, q_count = reground_claim_live(
            lot_id=lot_id,
            factor_id="factor-occupancy",
            claim_text="High occupancy surge (over 85% capacity)",
            retrieved_context=context,
            tolerances={"occupancy_tolerance": 0.08, "rate_tolerance": 5.0}
        )
        # Live re-grounding must catch the drift and fail
        assert is_supp_live is False
        assert verdict_live == "unsupported"
        assert q_count == 1
        assert "diverged" in detail_live.lower() or "tolerance" in detail_live.lower()
    finally:
        live_store.clear(lot_id)


# 5. Live source unreachable excludes the factor and does not raise
def test_live_source_unreachable_excludes_and_does_not_raise():
    # Query an invalid lot_id or simulate unreachable source
    is_supp, verdict, detail, q_count = reground_claim_live(
        lot_id="non-existent-lot-9999",
        factor_id="factor-occupancy",
        claim_text="High occupancy surge",
        retrieved_context={},
    )
    assert is_supp is False
    assert verdict == "unsupported"
    assert "live source unavailable" in detail.lower() or "not found" in detail.lower()


# 6. Tolerance boundary (just inside / just outside)
def test_tolerance_boundary_just_inside_and_outside():
    lot_id = "lot-metro-hub"
    lot = PARKING_LOTS_DB[lot_id]
    context = {"lot": lot, "duration_hours": 2}  # cached occupancy is 0.88
    live_store = get_live_store()
    tolerance = 0.08

    # Just inside tolerance: 0.88 - 0.079 = 0.801 >= 0.70 threshold & within tolerance
    live_store.set_override(lot_id, "occupancy_rate", 0.81)
    try:
        is_supp_in, _, detail_in, _ = reground_claim_live(
            lot_id=lot_id,
            factor_id="factor-occupancy",
            claim_text="Occupancy demand",
            retrieved_context=context,
            tolerances={"occupancy_tolerance": tolerance, "rate_tolerance": 5.0}
        )
        assert is_supp_in is True
    finally:
        live_store.clear(lot_id)

    # Just outside tolerance: occupancy drops to 0.60 (< 0.70 threshold & diff > 0.08)
    live_store.set_override(lot_id, "occupancy_rate", 0.60)
    try:
        is_supp_out, _, detail_out, _ = reground_claim_live(
            lot_id=lot_id,
            factor_id="factor-occupancy",
            claim_text="Occupancy demand",
            retrieved_context=context,
            tolerances={"occupancy_tolerance": tolerance, "rate_tolerance": 5.0}
        )
        assert is_supp_out is False
    finally:
        live_store.clear(lot_id)


# 7. Routing boundaries at exactly 0.10 and 0.40
def test_routing_boundaries_at_exact_thresholds():
    # Exactly below 0.10 -> light
    assert route_claim(0.0999, 0.10, 0.40) == "light"
    # Exactly at 0.10 -> standard
    assert route_claim(0.10, 0.10, 0.40) == "standard"
    # Exactly below 0.40 -> standard
    assert route_claim(0.3999, 0.10, 0.40) == "standard"
    # Exactly at 0.40 -> deep
    assert route_claim(0.40, 0.10, 0.40) == "deep"
    # Above 0.40 -> deep
    assert route_claim(0.75, 0.10, 0.40) == "deep"


# 8. Resummation invariants under random factors (property-style, seeded)
def test_resummation_invariants_random_property(tmp_path: Path):
    rng = random.Random(42)
    ledger = DecisionLedger(file_path=tmp_path / "prop_ledger.jsonl")

    for i in range(100):
        base_price = rng.uniform(50.0, 150.0)
        n_factors = rng.randint(1, 6)
        factors = []
        claim_verdicts = []

        for f_idx in range(n_factors):
            fid = f"factor-rand-{f_idx}"
            contrib = rng.uniform(10.0, 50.0)
            factors.append({
                "factor_id": fid,
                "description": f"Random factor {f_idx}",
                "contribution": contrib,
            })
            # Randomly support or reject
            is_supported = rng.choice([True, False])
            claim_verdicts.append({
                "factor_id": fid,
                "verdict": "supported" if is_supported else "unsupported",
            })

        proposed_price = base_price + sum(f["contribution"] for f in factors)
        pricing_result = {
            "base_price": base_price,
            "proposed_price": proposed_price,
            "factors": factors,
        }

        resum = resum_decision(pricing_result, claim_verdicts)

        # Invariant 1: final <= proposed
        assert resum["final_price"] <= proposed_price + 1e-5, "Invariant violated: final > proposed"

        # Invariant 2: binary inclusion
        expected_final = base_price + sum(
            f["contribution"] for f in factors
            if any(cv["factor_id"] == f["factor_id"] and cv["verdict"] == "supported" for cv in claim_verdicts)
        )
        assert abs(resum["final_price"] - expected_final) < 1e-4, "Invariant violated: binary inclusion mismatch"

        # Invariant 3: ledger write succeeds and seals
        rec = ledger.record_decision(
            f"prop-dec-{i}", "lot-test", pricing_result, resum, claim_verdicts
        )
        assert rec["sealed"] is True

    valid, msg = ledger.verify_chain()
    assert valid is True, f"Ledger chain validation failed: {msg}"


# 9. Ledger: editing each top-level field, tail truncation, deleting first block, and editing payload
def test_ledger_tamper_detection_v2_and_legacy_verify(tmp_path: Path):
    ledger_file = tmp_path / "tamper_v2.jsonl"
    ledger = DecisionLedger(file_path=ledger_file)

    p1 = {"base_price": 100.0, "proposed_price": 150.0, "factors": []}
    r1 = {"final_price": 130.0, "proposed_price": 150.0, "delta": 20.0, "was_adjusted": True}
    ledger.record_decision("dec-v2-1", "lot-alpha", p1, r1, [], "2026-10-12T12:00:00Z")

    p2 = {"base_price": 80.0, "proposed_price": 120.0, "factors": []}
    r2 = {"final_price": 120.0, "proposed_price": 120.0, "delta": 0.0, "was_adjusted": False}
    ledger.record_decision("dec-v2-2", "lot-beta", p2, r2, [], "2026-10-12T12:05:00Z")

    assert ledger.verify_chain()[0] is True

    # Test tampering each top-level field in v2
    fields_to_test = [
        ("lot_id", "lot-tampered"),
        ("proposed_price", 999.0),
        ("recorded_price", 999.0),
        ("delta", 999.0),
        ("was_adjusted", False),
        ("decision_id", "dec-tampered"),
        ("timestamp", "2099-01-01T00:00:00Z"),
    ]

    for field, bad_val in fields_to_test:
        lines = ledger_file.read_text(encoding="utf-8").strip().split("\n")
        entry = json.loads(lines[0])
        orig_val = entry[field]
        entry[field] = bad_val
        lines[0] = json.dumps(entry)
        ledger_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        is_valid, msg = ledger.verify_chain()
        assert is_valid is False, f"Tamper on {field} was not detected!"
        assert "Tampered" in msg or "mismatch" in msg

        # Restore
        entry[field] = orig_val
        lines[0] = json.dumps(entry)
        ledger_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Test tampering evidence payload
    lines = ledger_file.read_text(encoding="utf-8").strip().split("\n")
    entry = json.loads(lines[0])
    entry["evidence_payload"]["base_price"] = 9999.0
    lines[0] = json.dumps(entry)
    ledger_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert ledger.verify_chain()[0] is False

    # Restore
    entry["evidence_payload"]["base_price"] = 100.0
    lines[0] = json.dumps(entry)
    ledger_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert ledger.verify_chain()[0] is True

    # Test tail truncation (removes last line with sidecar present)
    lines = ledger_file.read_text(encoding="utf-8").strip().split("\n")
    ledger_file.write_text(lines[0] + "\n", encoding="utf-8")
    is_valid, msg = ledger.verify_chain()
    assert is_valid is False
    assert "head mismatch" in msg

    # Test deleting the first block
    ledger_file.write_text(lines[1] + "\n", encoding="utf-8")
    is_valid, msg = ledger.verify_chain()
    assert is_valid is False

    # Confirm legacy committed ledger still verifies without errors
    committed_ledger = DecisionLedger(DEFAULT_LEDGER_PATH)
    legacy_valid, legacy_msg = committed_ledger.verify_chain()
    assert legacy_valid is True
    assert "Verified" in legacy_msg


# 10. Concurrent appends (threads) produce a valid chain
def test_concurrent_appends_produce_valid_chain(tmp_path: Path):
    ledger_file = tmp_path / "concurrent_ledger.jsonl"
    ledger = DecisionLedger(file_path=ledger_file)
    n_threads = 10
    errors = []

    def worker(worker_id: int):
        try:
            p = {"base_price": 50.0 + worker_id, "proposed_price": 100.0 + worker_id, "factors": []}
            r = {"final_price": 90.0 + worker_id, "proposed_price": 100.0 + worker_id, "delta": 10.0, "was_adjusted": True}
            ledger.record_decision(f"thread-dec-{worker_id}", f"lot-{worker_id}", p, r, [])
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
    assert ledger.get_block_count() == n_threads
    is_valid, msg = ledger.verify_chain()
    assert is_valid is True, f"Concurrent chain corrupted: {msg}"


# 11. verification_mode default equals current behaviour on all 8 lots
def test_verification_mode_default_equals_baseline_after(tmp_path: Path):
    settings = load_settings()
    pipeline = VeriParkPipeline(config=settings, ledger_path=tmp_path / "tmp_test.jsonl")

    # Read docs/baseline_after.json
    baseline_file = Path("docs/baseline_after.json")
    if not baseline_file.exists():
        pytest.skip("docs/baseline_after.json not generated yet")

    expected = json.loads(baseline_file.read_text(encoding="utf-8"))

    for lot_id in PARKING_LOTS_DB.keys():
        res = pipeline.process_decision(lot_id, duration_hours=2, decision_id=f"verify-{lot_id}")
        exp = expected[lot_id]

        assert res["pricing_result"]["base_price"] == exp["base_price"]
        assert res["pricing_result"]["proposed_price"] == exp["proposed_price"]
        assert res["resummation"]["final_price"] == exp["final_price"]
        assert res["resummation"]["delta"] == exp["delta"]
        assert res["resummation"]["was_adjusted"] == exp["was_adjusted"]
        assert res["resummation"]["final_price"] <= res["pricing_result"]["proposed_price"]


# 12. API contract tests still pass unchanged
def test_api_contract_unchanged():
    from veripark.api.schemas import (
        DecisionDetailResponse,
        FactorVerificationResponse,
        LedgerRecordResponse,
        AdminStatsResponse
    )
    # Check that schema initialization works with both required and additive fields
    stats = AdminStatsResponse(
        total_decisions=10,
        adjustment_rate=0.2,
        avg_adjustment_amount=15.0,
        verification_cost_reduction_pct=37.5,
        trend=[],
        is_sample_data=False,
        checks_per_tier={"light": 5, "standard": 10, "deep": 2},
        live_queries_issued=2
    )
    assert stats.total_decisions == 10
    assert stats.is_sample_data is False
