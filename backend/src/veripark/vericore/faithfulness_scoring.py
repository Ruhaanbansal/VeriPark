"""Faithfulness scoring cascade orchestrating materiality-guided verification."""

from typing import List, Dict, Any
from veripark.vericore.materiality_scoring import compute_claim_materiality
from veripark.vericore.adaptive_routing import route_claim
from veripark.vericore.structured_evidence_assessment import evaluate_evidence_entailment
from veripark.vericore.live_regrounding import reground_claim_live
from veripark.api.schemas import ClaimVerdict

def verify_claims_cascade(
    claims: List[Dict[str, Any]],
    pricing_result: Dict[str, Any],
    lot_context: Dict[str, Any],
    config: Dict[str, Any] | None = None
) -> List[ClaimVerdict]:
    """Execute the VeriCore verification cascade.
    
    1. Compute materiality for each claim.
    2. Adaptively route to light, standard, or deep verification.
    3. Perform tier-specific verification (including Component 2 live re-grounding for deep).
    4. Return structured ClaimVerdict items.
    """
    cfg = config or {}
    mat_cfg = cfg.get("vericore", {}).get("materiality", {})
    light_thresh = mat_cfg.get("light_threshold", 0.10)
    std_thresh = mat_cfg.get("standard_threshold", 0.40)
    epsilon = mat_cfg.get("epsilon", 1e-6)

    proposed_price = pricing_result.get("proposed_price", 0.0)
    base_price = pricing_result.get("base_price", 0.0)
    lot_id = pricing_result.get("recommended_lot_id", "")

    verdicts: List[ClaimVerdict] = []

    for c in claims:
        claim_text = c.get("claim_text", "")
        fid = c.get("factor_id", "")
        contrib = c.get("contribution", 0.0)

        # 1. Compute materiality
        materiality = compute_claim_materiality(contrib, proposed_price, base_price, epsilon)

        # 2. Adaptive routing
        tier = route_claim(materiality, light_thresh, std_thresh)

        # 3. Execute tier verification
        if tier == "deep":
            # High-materiality: issue fresh live query to sensor
            is_supported, verdict, check_detail = reground_claim_live(lot_id, fid, claim_text)
        elif tier == "standard":
            # Standard: NLI + structured judge
            is_supported, nli_detail = evaluate_evidence_entailment(claim_text, fid, lot_context)
            if is_supported:
                verdict = "supported"
                check_detail = f"Careful check: NLI entailment and quantitative threshold verified. {nli_detail}"
            else:
                verdict = "unsupported"
                check_detail = f"Careful check failed: {nli_detail}"
        else:
            # Light: lightweight entailment check
            is_supported, nli_detail = evaluate_evidence_entailment(claim_text, fid, lot_context)
            verdict = "supported" if is_supported else "unsupported"
            check_detail = f"Quick check: {nli_detail}"

        verdicts.append(ClaimVerdict(
            claim_text=claim_text,
            factor_id=fid,
            materiality=materiality,
            tier=tier,
            verdict=verdict,
            check_detail=check_detail
        ))

    return verdicts
