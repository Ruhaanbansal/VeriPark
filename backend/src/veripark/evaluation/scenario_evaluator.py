"""Component 1-4 Empirical Evaluation Framework.

Provides reproducible scenario generation, baseline comparisons, ablations,
and metric calculation under controlled drift and phantom factor injections.
"""

import time
import copy
import random
from typing import Dict, Any, List, Tuple
from pathlib import Path

from veripark.data_sources.parking_lots import PARKING_LOTS_DB, _init_lots
from veripark.data_sources.live_state import LiveStateStore, DriftInjector, get_live_store
from veripark.vericore.materiality_scoring import compute_claim_materiality
from veripark.vericore.adaptive_routing import route_claim
from veripark.vericore.decision_resummation import resum_decision
from veripark.vericore.faithfulness_scoring import verify_claims_cascade
from veripark.agents.allocation_pricing_agent import AllocationPricingAgent
from veripark.agents.explanation_drafting_agent import ExplanationDraftingAgent
from veripark.vericore.claim_extraction import extract_and_bind_claims

_init_lots()

METHODS = [
    "B1_none",
    "B2_uniform_light",
    "B3_uniform_deep",
    "VeriCore",
    "VeriCore_no_live",
    "Ablation_thresh_05_30",
    "Ablation_thresh_20_50",
]

DRIFT_LEVELS = [0.0, 0.10, 0.20, 0.30]


def get_method_config(method: str) -> Dict[str, Any]:
    """Builds pipeline config dictionary for a given method or ablation."""
    cfg = {
        "vericore": {
            "verification_mode": "vericore",
            "materiality": {
                "light_threshold": 0.10,
                "standard_threshold": 0.40,
                "epsilon": 1e-6,
            },
            "live_regrounding": {
                "occupancy_tolerance": 0.08,
                "rate_tolerance": 5.0,
                "timeout_seconds": 3.0,
            },
            "resummation": {
                "enforce_clamping_invariant": True,
                "allow_partial_credit": False,
            },
            "evaluation": {
                "cost_units": {
                    "deep": 1.0,
                    "standard": 0.3,
                    "light": 0.05,
                }
            }
        }
    }

    if method == "B1_none":
        cfg["vericore"]["verification_mode"] = "none"
    elif method == "B2_uniform_light":
        cfg["vericore"]["verification_mode"] = "uniform_light"
    elif method == "B3_uniform_deep":
        cfg["vericore"]["verification_mode"] = "uniform_deep"
    elif method == "VeriCore_no_live":
        cfg["vericore"]["verification_mode"] = "vericore_no_live"
    elif method == "Ablation_thresh_05_30":
        cfg["vericore"]["verification_mode"] = "vericore"
        cfg["vericore"]["materiality"]["light_threshold"] = 0.05
        cfg["vericore"]["materiality"]["standard_threshold"] = 0.30
    elif method == "Ablation_thresh_20_50":
        cfg["vericore"]["verification_mode"] = "vericore"
        cfg["vericore"]["materiality"]["light_threshold"] = 0.20
        cfg["vericore"]["materiality"]["standard_threshold"] = 0.50

    return cfg


def run_scenario(
    lot_id: str,
    method: str,
    drift_level: float,
    rng: random.Random,
    inject_phantom: bool = True
) -> Dict[str, Any]:
    """Runs a single evaluation scenario under the specified method and drift."""
    lot = copy.deepcopy(PARKING_LOTS_DB[lot_id])
    lot_context = {"lot": lot, "duration_hours": 2}
    pricing_agent = AllocationPricingAgent()
    drafting_agent = ExplanationDraftingAgent()

    pricing_result = pricing_agent.propose_pricing(lot_context)
    factors = list(pricing_result.get("factors", []))
    base_price = float(pricing_result.get("base_price", 0.0))

    # Ground-truth validity tracking
    ground_truth_valid = {}
    is_drift_invalidated = {}

    for f in factors:
        fid = f["factor_id"]
        # In base synthetic dataset, identify factors with ground-truth defects
        if "unverified" in fid:
            ground_truth_valid[fid] = False
        elif fid == "factor-event" and not lot.get("live_signals", {}).get("event_schedule_verified", True):
            ground_truth_valid[fid] = False
        elif fid == "factor-occupancy":
            cam = lot.get("live_signals", {}).get("camera_verified_available")
            sensor = lot.get("live_signals", {}).get("sensor_reported_available")
            if cam is not None and sensor is not None and cam > sensor:
                ground_truth_valid[fid] = False
            else:
                ground_truth_valid[fid] = True
        else:
            ground_truth_valid[fid] = True
        is_drift_invalidated[fid] = False

    # (a) Inject phantom factor (known invalid)
    phantom_fid = None
    if inject_phantom:
        phantom_contrib = rng.choice([15.0, 20.0, 25.0, 30.0])
        phantom_fid = f"factor-unverified-phantom-{rng.randint(100, 999)}"
        phantom_factor = {
            "factor_id": phantom_fid,
            "description": "Unverified emergency peak congestion surcharge",
            "contribution": phantom_contrib,
            "confidence": 0.50,
        }
        factors.append(phantom_factor)
        pricing_result["factors"] = factors
        pricing_result["proposed_price"] = base_price + sum(f["contribution"] for f in factors)
        ground_truth_valid[phantom_fid] = False
        is_drift_invalidated[phantom_fid] = False

    # (b) Apply live drift via DriftInjector
    live_store = get_live_store()
    live_store.clear(lot_id)
    if drift_level > 0.0:
        drift_seed = rng.randint(1, 1000000)
        injector = DriftInjector(fraction=drift_level, seed=drift_seed)
        injector.apply(live_store, lot_id, lot)

        # Check if drift invalidated any previously valid factor
        signals = lot.get("live_signals", {})
        live_occ = live_store.get_field(lot_id, "occupancy_rate")
        if live_occ is not None and "factor-occupancy" in ground_truth_valid:
            if live_occ < 0.70 and ground_truth_valid["factor-occupancy"]:
                ground_truth_valid["factor-occupancy"] = False
                is_drift_invalidated["factor-occupancy"] = True

        live_evt = live_store.get_field(lot_id, "event_schedule_verified")
        if live_evt is False and "factor-event" in ground_truth_valid:
            if ground_truth_valid["factor-event"]:
                ground_truth_valid["factor-event"] = False
                is_drift_invalidated["factor-event"] = True

        live_wtr = live_store.get_field(lot_id, "weather")
        if live_wtr == "Clear" and "factor-weather" in ground_truth_valid:
            if ground_truth_valid["factor-weather"]:
                ground_truth_valid["factor-weather"] = False
                is_drift_invalidated["factor-weather"] = True

    # Calculate Ground-Truth Price: base + sum of truly valid factors
    ground_truth_price = base_price + sum(
        f["contribution"] for f in factors if ground_truth_valid.get(f["factor_id"], False)
    )

    claims = drafting_agent.draft_explanation(pricing_result, lot_context)
    if phantom_fid:
        claims.append({
            "claim_text": "Unverified emergency peak congestion surcharge applied.",
            "factor_id": phantom_fid
        })
    bound_claims = extract_and_bind_claims(claims, pricing_result["factors"])
    cfg = get_method_config(method)

    start_time = time.perf_counter()
    verdicts, metrics = verify_claims_cascade(bound_claims, pricing_result, lot_context, config=cfg)
    resum_result = resum_decision(pricing_result, verdicts)
    wall_time = time.perf_counter() - start_time

    # Cleanup live state overrides
    live_store.clear(lot_id)

    proposed_price = pricing_result["proposed_price"]
    final_price = resum_result["final_price"]

    # Invariant checks
    final_gt_proposed_violation = 1 if final_price > proposed_price + 1e-5 else 0
    final_gt_truth = 1 if final_price > ground_truth_price + 1e-5 else 0

    excluded_factors = set(resum_result.get("excluded_factors", []))

    # Metric: phantom factor caught
    phantom_caught = 0
    if phantom_fid:
        phantom_caught = 1 if phantom_fid in excluded_factors else 0

    # Metric: false exclusions (valid factors wrongly excluded)
    valid_factors = [f["factor_id"] for f in factors if ground_truth_valid.get(f["factor_id"], False)]
    false_exclusions = sum(1 for fid in valid_factors if fid in excluded_factors)

    # Metric: drift caught (factors invalidated by drift that were excluded)
    drifted_factors = [fid for fid, is_d in is_drift_invalidated.items() if is_d]
    drift_caught = sum(1 for fid in drifted_factors if fid in excluded_factors)

    cost_units = cfg["vericore"]["evaluation"]["cost_units"]
    checks = metrics.get("checks_per_tier", {})
    cost = (
        checks.get("deep", 0) * cost_units.get("deep", 1.0) +
        checks.get("standard", 0) * cost_units.get("standard", 0.3) +
        checks.get("light", 0) * cost_units.get("light", 0.05)
    )

    return {
        "method": method,
        "drift_level": drift_level,
        "proposed_price": proposed_price,
        "final_price": final_price,
        "ground_truth_price": ground_truth_price,
        "price_error": abs(final_price - ground_truth_price),
        "was_adjusted": resum_result["was_adjusted"],
        "delta": resum_result["delta"],
        "final_gt_proposed_violation": final_gt_proposed_violation,
        "final_gt_truth": final_gt_truth,
        "phantom_injected": 1 if phantom_fid else 0,
        "phantom_caught": phantom_caught,
        "valid_factors_count": len(valid_factors),
        "false_exclusions": false_exclusions,
        "drifted_factors_count": len(drifted_factors),
        "drift_caught": drift_caught,
        "checks_run": sum(checks.values()),
        "live_queries_issued": metrics.get("live_queries_issued", 0),
        "assumed_cost": cost,
        "wall_time": wall_time,
    }
