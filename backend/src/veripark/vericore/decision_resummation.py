"""Component 3 (Patent-Critical): Decomposed-Factor Decision Resummation.

Strict arithmetic recalculation of decision value based exclusively on verified
claims. If an unverified claim is detected, the underlying decision itself is
mechanically clamped/recomputed to the maximum justifiable amount.

INVARIANTS:
1. final_price never exceeds proposed_price.
2. Factor inclusion is binary (no partial credit).
3. Exact arithmetic decomposition (no generic confidence or evidence-grade gate).
"""

from typing import Dict, Any, List, Set

def resum_decision(pricing_result: Any, claim_verdicts: List[Any]) -> Dict[str, Any]:
    """Mechanically recalculate and clamp the decision value from verified factors.
    
    Exact arithmetic mechanism specified in Section 6.3:
    """
    # Extract verified factor IDs (supported or live_reverified)
    verified_factor_ids: Set[str] = set()
    for c in claim_verdicts:
        verdict = getattr(c, "verdict", None) if hasattr(c, "verdict") else c.get("verdict")
        factor_id = getattr(c, "factor_id", None) if hasattr(c, "factor_id") else c.get("factor_id")
        if verdict in ("supported", "live_reverified"):
            verified_factor_ids.add(factor_id)

    base_price = getattr(pricing_result, "base_price", None)
    if base_price is None:
        base_price = pricing_result["base_price"]

    proposed_price = getattr(pricing_result, "proposed_price", None)
    if proposed_price is None:
        proposed_price = pricing_result["proposed_price"]

    factors = getattr(pricing_result, "factors", None)
    if factors is None:
        factors = pricing_result["factors"]

    # Strict binary inclusion: sum only contributions whose factors are verified
    resummed_price = base_price
    for f in factors:
        fid = getattr(f, "factor_id", None) if hasattr(f, "factor_id") else f["factor_id"]
        contrib = getattr(f, "contribution", None) if hasattr(f, "contribution") else f["contribution"]
        if fid in verified_factor_ids:
            resummed_price += contrib

    # Invariant 1: final_price never exceeds proposed_price
    final_price = min(float(resummed_price), float(proposed_price))
    delta = round(float(proposed_price - final_price), 2)
    
    excluded_factors = []
    for f in factors:
        fid = getattr(f, "factor_id", None) if hasattr(f, "factor_id") else f["factor_id"]
        if fid not in verified_factor_ids:
            excluded_factors.append(fid)

    return {
        "final_price": final_price,
        "proposed_price": proposed_price,
        "delta": delta,
        "excluded_factors": excluded_factors,
        "was_adjusted": delta > 0
    }
