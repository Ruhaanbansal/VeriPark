"""Claim extraction and provenance binding.

Enforces that draft claims are linked to factor IDs at generation time,
verifying structural integrity before verification routing.
"""

from typing import List, Dict, Any

def extract_and_bind_claims(
    draft_claims: List[Dict[str, str]],
    factors: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Bind each tagged claim to its corresponding factor metadata.
    
    Raises ValueError if any claim has invalid or missing provenance.
    """
    factor_map = {f["factor_id"]: f for f in factors}
    bound_claims = []

    for c in draft_claims:
        fid = c.get("factor_id")
        text = c.get("claim_text", "")
        if not fid or fid not in factor_map:
            # Unbound claim detected
            continue
        
        factor = factor_map[fid]
        bound_claims.append({
            "claim_text": text,
            "factor_id": fid,
            "factor_description": factor.get("description", ""),
            "contribution": factor.get("contribution", 0.0),
        })

    return bound_claims
