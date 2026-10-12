"""Faithfulness scoring cascade orchestrating materiality-guided verification.

Implements C1 (materiality routing), C2 (live re-grounding for deep tier),
and provides per-decision metrics: checks_per_tier, live_queries_issued.
"""

from typing import List, Dict, Any, Tuple
from veripark.vericore.materiality_scoring import compute_claim_materiality
from veripark.vericore.adaptive_routing import route_claim
from veripark.vericore.structured_evidence_assessment import evaluate_evidence_entailment
from veripark.vericore.live_regrounding import reground_claim_live
from veripark.api.schemas import ClaimVerdict


def verify_claims_cascade(
    claims: List[Dict[str, Any]],
    pricing_result: Dict[str, Any],
    lot_context: Dict[str, Any],
    config: Dict[str, Any] | None = None,
) -> Tuple[List[ClaimVerdict], Dict[str, Any]]:
    """Execute the VeriCore verification cascade and return verdicts + metrics.

    Returns:
        (verdicts, metrics)
        metrics keys: checks_per_tier (dict), live_queries_issued (int)

    Routing:
        light    < light_threshold (0.10)  : cached entailment, quick check
        standard < standard_threshold (0.40): cached entailment + structured judge
        deep    >= standard_threshold       : live re-grounding (C2)
    """
    cfg = config or {}
    mat_cfg = cfg.get("vericore", {}).get("materiality", {})
    light_thresh = mat_cfg.get("light_threshold", 0.10)
    std_thresh = mat_cfg.get("standard_threshold", 0.40)
    epsilon = mat_cfg.get("epsilon", 1e-6)

    lr_cfg = cfg.get("vericore", {}).get("live_regrounding", {})
    tolerances = {
        "occupancy_tolerance": lr_cfg.get("occupancy_tolerance", 0.08),
        "rate_tolerance": lr_cfg.get("rate_tolerance", 5.0),
    }

    proposed_price = pricing_result.get("proposed_price", 0.0)
    base_price = pricing_result.get("base_price", 0.0)
    lot_id = pricing_result.get("recommended_lot_id", "")

    verdicts: List[ClaimVerdict] = []
    checks_per_tier: Dict[str, int] = {"light": 0, "standard": 0, "deep": 0}
    live_queries_issued: int = 0

    for c in claims:
        claim_text = c.get("claim_text", "")
        fid = c.get("factor_id", "")
        contrib = c.get("contribution", 0.0)

        # C1: Compute materiality and route to verification tier
        materiality = compute_claim_materiality(contrib, proposed_price, base_price, epsilon)
        tier = route_claim(materiality, light_thresh, std_thresh)
        checks_per_tier[tier] = checks_per_tier.get(tier, 0) + 1

        if tier == "deep":
            # C2: High-materiality — issue fresh live query to originating sensor
            is_supported, verdict, check_detail, n_queries = reground_claim_live(
                lot_id,
                fid,
                claim_text,
                retrieved_context=lot_context,
                tolerances=tolerances,
            )
            live_queries_issued += n_queries
            check_detail = f"Rechecked live just now: {check_detail}" if not check_detail.startswith("Rechecked") else check_detail

        elif tier == "standard":
            # Standard: NLI + structured judge against cached context
            is_supported, nli_detail = evaluate_evidence_entailment(
                claim_text, fid, lot_context
            )
            if is_supported:
                verdict = "supported"
                check_detail = f"Careful check: NLI entailment verified. {nli_detail}"
            else:
                verdict = "unsupported"
                check_detail = f"Careful check failed: {nli_detail}"

        else:
            # Light: lightweight cached entailment check
            is_supported, nli_detail = evaluate_evidence_entailment(
                claim_text, fid, lot_context
            )
            verdict = "supported" if is_supported else "unsupported"
            check_detail = f"Quick check: {nli_detail}"

        verdicts.append(ClaimVerdict(
            claim_text=claim_text,
            factor_id=fid,
            materiality=materiality,
            tier=tier,
            verdict=verdict,
            check_detail=check_detail,
        ))

    metrics = {
        "checks_per_tier": checks_per_tier,
        "live_queries_issued": live_queries_issued,
    }
    return verdicts, metrics
