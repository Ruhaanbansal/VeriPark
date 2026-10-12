"""Component 1-4 Empirical Evaluation Framework.

Provides reproducible scenario generation, baseline comparisons, ablations,
and metric calculation under controlled drift and realistic phantom factor injections.
"""

import time
import copy
import random
from typing import Dict, Any, List, Tuple
from pathlib import Path

from veripark.data_sources.parking_lots import PARKING_LOTS_DB, _init_lots
from veripark.data_sources.live_state import LiveStateStore, DriftInjector, get_live_store
from veripark.vericore.decision_resummation import resum_decision
from veripark.vericore.faithfulness_scoring import verify_claims_cascade
from veripark.agents.allocation_pricing_agent import AllocationPricingAgent
from veripark.agents.explanation_drafting_agent import ExplanationDraftingAgent
from veripark.vericore.claim_extraction import extract_and_bind_claims
from veripark.evaluation.ground_truth import is_factor_ground_truth_valid

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

PHANTOM_CLASSES = ["control", "registry_rejected", "content_false"]


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
            "rules": {
                "surge_threshold": 0.70,
                "event_radius_m": 500,
            },
            "live_regrounding": {
                "occupancy_tolerance": 0.08,
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


def _generate_phantom_factor(
    phantom_class: str,
    lot: Dict[str, Any],
    rng: random.Random
) -> Tuple[Dict[str, Any] | None, Dict[str, Any] | None]:
    """Generate a realistic phantom factor and its corresponding drafted claim.

    Classes:
    (a) 'registry_rejected': unregistered factor type (design-property test, not content detection).
    (b) 'content_false': registered factor type with demonstrably false content.
    (c) 'control': no phantom injected.

    Important: Phantom IDs must not contain words 'unverified', 'phantom', or 'fake'.
    """
    if phantom_class in ("control", "none"):
        return None, None

    signals = lot.get("live_signals", {})

    if phantom_class == "registry_rejected":
        # Class (a): Unregistered factor type.
        # Tested by fail-closed verifier registry.
        suffix = rng.randint(100, 999)
        fid = f"factor-civic-access-{suffix}"
        contrib = rng.choice([15.0, 20.0, 25.0, 30.0])
        factor = {
            "factor_id": fid,
            "description": "Municipal low-emission zone civic staging surcharge",
            "contribution": contrib,
            "confidence": 0.60,
        }
        claim = {
            "factor_id": fid,
            "claim_text": "Municipal low-emission zone staging surcharge applied per municipal schedule.",
        }
        return factor, claim

    elif phantom_class == "content_false":
        # Class (b): Registered factor type, but claim is demonstrably false.
        # Tested by content entailment verifier (B2 / cached NLI).
        suffix = rng.randint(100, 999)
        weather = str(signals.get("weather", ""))
        occ = signals.get("occupancy_rate", 0.0)

        # Pick a false factor dimension that contradicts this lot's actual state
        if "Rain" not in weather:
            # Weather is Clear / not rainy -> inject false rain factor
            fid = f"factor-weather-monsoon-{suffix}"
            contrib = 15.0
            factor = {
                "factor_id": fid,
                "description": "Precipitation protection surge during active monsoon warning",
                "contribution": contrib,
                "confidence": 0.50,
            }
            claim = {
                "factor_id": fid,
                "claim_text": "Active heavy monsoon rain advisory in precinct warrants covered premium.",
            }
        elif occ < 0.70:
            # Occupancy is below surge threshold -> inject false high occupancy surge
            fid = f"factor-occupancy-demand-{suffix}"
            contrib = 20.0
            factor = {
                "factor_id": fid,
                "description": "Peak rush demand surge (occupancy exceeds 85%)",
                "contribution": contrib,
                "confidence": 0.50,
            }
            claim = {
                "factor_id": fid,
                "claim_text": "High occupancy surge applied: facility capacity utilization exceeds 85%.",
            }
        else:
            # High occupancy and rainy -> inject false event factor
            fid = f"factor-event-marathon-{suffix}"
            contrib = 25.0
            factor = {
                "factor_id": fid,
                "description": "Major international marathon expo surge within 200m",
                "contribution": contrib,
                "confidence": 0.50,
            }
            claim = {
                "factor_id": fid,
                "claim_text": "International athletics expo confirmed active 150m from facility entrance.",
            }
        return factor, claim

    return None, None


def run_scenario(
    lot_id: str,
    method: str,
    drift_level: float,
    rng: random.Random,
    phantom_class: str = "control"
) -> Dict[str, Any]:
    """Runs a single evaluation scenario under specified method, drift, and phantom class."""
    cfg = get_method_config(method)
    rules = cfg["vericore"]["rules"]
    tolerances = cfg["vericore"]["live_regrounding"]

    lot = copy.deepcopy(PARKING_LOTS_DB[lot_id])
    lot_context = {"lot": lot, "duration_hours": 2}
    pricing_agent = AllocationPricingAgent()
    drafting_agent = ExplanationDraftingAgent()

    pricing_result = pricing_agent.propose_pricing(lot_context)
    factors = list(pricing_result.get("factors", []))
    base_price = float(pricing_result.get("base_price", 0.0))

    # (a) Inject realistic phantom if requested
    phantom_factor, phantom_claim = _generate_phantom_factor(phantom_class, lot, rng)
    phantom_fid = None
    if phantom_factor:
        phantom_fid = phantom_factor["factor_id"]
        factors.append(phantom_factor)
        pricing_result["factors"] = factors
        pricing_result["proposed_price"] = base_price + sum(f["contribution"] for f in factors)

    # (b) Apply live drift via DriftInjector to simulate world state divergence
    live_store = get_live_store()
    live_store.clear(lot_id)
    if drift_level > 0.0:
        drift_seed = rng.randint(1, 1000000)
        injector = DriftInjector(fraction=drift_level, seed=drift_seed)
        injector.apply(live_store, lot_id, lot)

    # Build effective live signals dictionary representing the world state after drift
    snapshot_signals = lot.get("live_signals", {})
    effective_signals = dict(snapshot_signals)
    for field in [
        "occupancy_rate",
        "nearby_event",
        "event_schedule_verified",
        "event_distance_m",
        "weather",
        "camera_verified_available",
        "sensor_reported_available",
    ]:
        override = live_store.get_field(lot_id, field)
        if override is not None:
            effective_signals[field] = override

    # Ground-truth validity determination for every factor
    ground_truth_valid = {}
    is_drift_invalidated = {}

    for f in factors:
        fid = f["factor_id"]
        is_ph = (fid == phantom_fid)

        # Validity prior to drift injection
        pre_drift_valid = is_factor_ground_truth_valid(
            factor=f,
            lot=lot,
            live_signals=snapshot_signals,
            claimed_signals=snapshot_signals,
            is_phantom=is_ph,
            rules=rules,
            tolerances=tolerances,
        )

        # Validity in the actual world state after drift
        post_drift_valid = is_factor_ground_truth_valid(
            factor=f,
            lot=lot,
            live_signals=effective_signals,
            claimed_signals=snapshot_signals,
            is_phantom=is_ph,
            rules=rules,
            tolerances=tolerances,
        )

        ground_truth_valid[fid] = post_drift_valid
        is_drift_invalidated[fid] = (pre_drift_valid and not post_drift_valid)

    # Calculate Ground-Truth Price: base + sum of truly valid factors in world state
    ground_truth_price = base_price + sum(
        f["contribution"] for f in factors if ground_truth_valid.get(f["factor_id"], False)
    )

    claims = drafting_agent.draft_explanation(pricing_result, lot_context)
    if phantom_claim:
        claims.append(phantom_claim)

    bound_claims = extract_and_bind_claims(claims, pricing_result["factors"])

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

    # Metric: phantom factor caught per class
    phantom_class_a_injected = 1 if phantom_class == "registry_rejected" else 0
    phantom_class_a_caught = 1 if (phantom_class == "registry_rejected" and phantom_fid in excluded_factors) else 0

    phantom_class_b_injected = 1 if phantom_class == "content_false" else 0
    phantom_class_b_caught = 1 if (phantom_class == "content_false" and phantom_fid in excluded_factors) else 0

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
        "phantom_class": phantom_class,
        "proposed_price": proposed_price,
        "final_price": final_price,
        "ground_truth_price": ground_truth_price,
        "price_error": abs(final_price - ground_truth_price),
        "was_adjusted": resum_result["was_adjusted"],
        "delta": resum_result["delta"],
        "final_gt_proposed_violation": final_gt_proposed_violation,
        "final_gt_truth": final_gt_truth,
        "phantom_class_a_injected": phantom_class_a_injected,
        "phantom_class_a_caught": phantom_class_a_caught,
        "phantom_class_b_injected": phantom_class_b_injected,
        "phantom_class_b_caught": phantom_class_b_caught,
        "valid_factors_count": len(valid_factors),
        "false_exclusions": false_exclusions,
        "drifted_factors_count": len(drifted_factors),
        "drift_caught": drift_caught,
        "checks_run": sum(checks.values()),
        "live_queries_issued": metrics.get("live_queries_issued", 0),
        "assumed_cost": cost,
        "wall_time": wall_time,
    }
