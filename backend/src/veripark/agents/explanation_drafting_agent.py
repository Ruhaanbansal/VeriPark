from typing import Dict, Any, List

class ExplanationDraftingAgent:
    """Stage 3: Writes a natural-language explanation where every atomic claim
    is tagged at generation time with the specific pricing factor ID it justifies.

    Required output contract:
    [{"claim_text": str, "factor_id": str}, ...]
    """

    def draft_explanation(self, pricing_result: Dict[str, Any], lot_context: Dict[str, Any]) -> List[Dict[str, str]]:
        factors = pricing_result.get("factors", [])
        claims: List[Dict[str, str]] = []

        for f in factors:
            fid = f["factor_id"]
            contrib = f["contribution"]
            desc = f["description"]

            if fid == "factor-occupancy":
                claim_text = (
                    f"Occupancy is currently surging past 85% capacity with only 14 spots left, "
                    f"adding ₹{int(contrib)} to reflect tight peak demand."
                )
            elif fid == "factor-event":
                claim_text = (
                    f"An active public event is taking place within 200m of the parking deck, "
                    f"adding a ₹{int(contrib)} event proximity adjustment."
                )
            elif fid == "factor-weather":
                claim_text = (
                    f"A local heavy rain warning is active, increasing demand for covered underground bays "
                    f"by ₹{int(contrib)}."
                )
            elif fid == "factor-festival-surcharge":
                # Intentionally ungrounded / hallucinated claim by the drafting model
                claim_text = (
                    f"A special city street fair exclusion zone has closed adjacent roads, "
                    f"requiring an additional ₹{int(contrib)} traffic mitigation surcharge."
                )
            elif fid == "factor-ev-premium":
                claim_text = (
                    f"Includes priority access lane and dedicated EV-ready bay reservation for ₹{int(contrib)}."
                )
            else:
                claim_text = f"{desc} accounts for a ₹{int(contrib)} adjustment to the baseline rate."

            claims.append({
                "claim_text": claim_text,
                "factor_id": fid
            })

        return claims
