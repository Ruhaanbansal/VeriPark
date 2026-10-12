"""Step 6 Sanity Tests for VeriCore Evaluation and Verifier Hardening.

Covers:
1. Zero drift, control class: false-exclusion rate == 0 and mean price error == 0 for B2, B3, VeriCore.
2. Class (b) phantoms are caught by B2 (cached content check), proving detection is by content.
3. Class (a) phantoms are caught by fail-closed registry and reported separately.
4. B1 cost and checks == 0 and every proposed factor accepted.
5. Timeout test: a fetch that sleeps longer than timeout_seconds returns unsupported without raising.
6. Sensor-discrepancy live branch returns supported when camera <= sensor and unsupported when camera > sensor.
7. Occupancy live rule: inside tolerance and above threshold supported; outside tolerance unsupported; below threshold unsupported.
"""

import time
import random
import pytest

from veripark.data_sources.parking_lots import PARKING_LOTS_DB, _init_lots
from veripark.evaluation.scenario_evaluator import run_scenario
from veripark.vericore.live_regrounding import reground_claim_live

_init_lots()


def test_zero_drift_control_agreement_b2_b3_vericore():
    """1. At 0% drift, control class: false-exclusion rate == 0 and mean price error == 0 for B2, B3 and VeriCore."""
    rng = random.Random(42)
    for method in ["B2_uniform_light", "B3_uniform_deep", "VeriCore"]:
        for lot_id in PARKING_LOTS_DB.keys():
            res = run_scenario(lot_id, method, drift_level=0.0, rng=rng, phantom_class="control")
            assert res["false_exclusions"] == 0, f"False exclusions occurred for {method} on {lot_id}"
            assert res["price_error"] == 0.0, f"Price error occurred for {method} on {lot_id}: {res['price_error']}"


def test_class_b_phantoms_caught_by_b2_content_check():
    """2. Class (b) phantoms are caught by B2 (cached content check), proving detection is by content."""
    rng = random.Random(101)
    for lot_id in PARKING_LOTS_DB.keys():
        res = run_scenario(lot_id, "B2_uniform_light", drift_level=0.0, rng=rng, phantom_class="content_false")
        assert res["phantom_class_b_injected"] == 1
        assert res["phantom_class_b_caught"] == 1, f"B2 failed to catch Class (b) content-false phantom on {lot_id}"


def test_class_a_phantoms_caught_by_fail_closed_registry():
    """3. Class (a) is caught by fail-closed registry and reported separately."""
    rng = random.Random(2024)
    for lot_id in PARKING_LOTS_DB.keys():
        res = run_scenario(lot_id, "VeriCore", drift_level=0.0, rng=rng, phantom_class="registry_rejected")
        assert res["phantom_class_a_injected"] == 1
        assert res["phantom_class_a_caught"] == 1, f"Fail-closed registry failed to catch Class (a) on {lot_id}"


def test_b1_cost_and_checks_zero_and_all_factors_accepted():
    """4. B1 cost and checks == 0 and every proposed factor accepted."""
    rng = random.Random(42)
    for lot_id in PARKING_LOTS_DB.keys():
        res = run_scenario(lot_id, "B1_none", drift_level=0.10, rng=rng, phantom_class="content_false")
        assert res["checks_run"] == 0
        assert res["assumed_cost"] == 0.0
        assert res["live_queries_issued"] == 0
        assert res["final_price"] == res["proposed_price"]
        assert res["was_adjusted"] is False


def test_timeout_returns_unsupported_without_raising(monkeypatch):
    """5. Timeout test: a fetch that sleeps longer than timeout_seconds returns unsupported without raising."""
    def slow_fetch(lot_id, claim_type):
        time.sleep(0.08)
        return {"status": "ok"}

    monkeypatch.setattr("veripark.vericore.live_regrounding.fetch_live_data_source", slow_fetch)

    is_supp, verdict, detail, q_count = reground_claim_live(
        lot_id="lot-metro-hub",
        factor_id="factor-occupancy",
        claim_text="Occupancy claim",
        timeout_seconds=0.01,
    )
    assert is_supp is False
    assert verdict == "unsupported"
    assert "timeout" in detail or "unavailable" in detail
    assert q_count == 1


def test_sensor_discrepancy_live_branch(monkeypatch):
    """6. Sensor-discrepancy live branch returns supported when camera <= sensor and unsupported when camera > sensor."""
    # Case 1: camera <= sensor -> supported
    monkeypatch.setattr(
        "veripark.vericore.live_regrounding.fetch_live_data_source",
        lambda lot_id, claim_type: {
            "type": "occupancy",
            "camera_verified_available": 10,
            "sensor_reported_available": 15,
            "status": "ok",
        }
    )
    is_supp, verdict, detail, q_count = reground_claim_live(
        lot_id="lot-express-deck",
        factor_id="factor-sensor-discrepancy",
        claim_text="Sensor mismatch",
    )
    assert is_supp is True
    assert verdict == "live_reverified"
    assert q_count == 1

    # Case 2: camera > sensor -> unsupported
    monkeypatch.setattr(
        "veripark.vericore.live_regrounding.fetch_live_data_source",
        lambda lot_id, claim_type: {
            "type": "occupancy",
            "camera_verified_available": 25,
            "sensor_reported_available": 10,
            "status": "ok",
        }
    )
    is_supp, verdict, detail, q_count = reground_claim_live(
        lot_id="lot-express-deck",
        factor_id="factor-sensor-discrepancy",
        claim_text="Sensor mismatch",
    )
    assert is_supp is False
    assert verdict == "unsupported"
    assert q_count == 1


def test_occupancy_live_rule(monkeypatch):
    """7. Occupancy live rule: inside tolerance and above threshold supported; outside tolerance unsupported; below threshold unsupported."""
    context = {"lot": {"live_signals": {"occupancy_rate": 0.85}}}

    # Case A: inside tolerance (live 0.86, cached 0.85, diff 0.01 <= 0.08) and above threshold (0.86 >= 0.70) -> supported
    monkeypatch.setattr(
        "veripark.vericore.live_regrounding.fetch_live_data_source",
        lambda lot_id, claim_type: {
            "type": "occupancy",
            "live_occupancy_rate": 0.86,
            "live_spots_available": 15,
            "status": "ok",
        }
    )
    is_supp, verdict, _, _ = reground_claim_live(
        lot_id="lot-metro-hub",
        factor_id="factor-occupancy",
        claim_text="Occupancy claim",
        retrieved_context=context,
        tolerances={"occupancy_tolerance": 0.08},
        rules={"surge_threshold": 0.70},
    )
    assert is_supp is True
    assert verdict == "live_reverified"

    # Case B: outside tolerance (live 0.72, cached 0.85, diff 0.13 > 0.08) -> unsupported
    monkeypatch.setattr(
        "veripark.vericore.live_regrounding.fetch_live_data_source",
        lambda lot_id, claim_type: {
            "type": "occupancy",
            "live_occupancy_rate": 0.72,
            "live_spots_available": 30,
            "status": "ok",
        }
    )
    is_supp, verdict, detail, _ = reground_claim_live(
        lot_id="lot-metro-hub",
        factor_id="factor-occupancy",
        claim_text="Occupancy claim",
        retrieved_context=context,
        tolerances={"occupancy_tolerance": 0.08},
        rules={"surge_threshold": 0.70},
    )
    assert is_supp is False
    assert verdict == "unsupported"
    assert "diverged" in detail

    # Case C: inside tolerance (live 0.68, cached 0.69, diff 0.01 <= 0.08) but below threshold (0.68 < 0.70) -> unsupported
    context_low = {"lot": {"live_signals": {"occupancy_rate": 0.69}}}
    monkeypatch.setattr(
        "veripark.vericore.live_regrounding.fetch_live_data_source",
        lambda lot_id, claim_type: {
            "type": "occupancy",
            "live_occupancy_rate": 0.68,
            "live_spots_available": 40,
            "status": "ok",
        }
    )
    is_supp, verdict, detail, _ = reground_claim_live(
        lot_id="lot-metro-hub",
        factor_id="factor-occupancy",
        claim_text="Occupancy claim",
        retrieved_context=context_low,
        tolerances={"occupancy_tolerance": 0.08},
        rules={"surge_threshold": 0.70},
    )
    assert is_supp is False
    assert verdict == "unsupported"
    assert "below surge threshold" in detail
