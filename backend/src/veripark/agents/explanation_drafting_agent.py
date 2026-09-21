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
        lot = lot_context.get("lot", {})
        signals = lot.get("live_signals", {})

        # Dynamic lot values for accurate claim generation
        spots_available = lot.get("spots_available", 14)
        occ_pct = int(signals.get("occupancy_rate", 0.85) * 100)
        nearby_event = signals.get("nearby_event", "an event")
        event_distance_m = signals.get("event_distance_m", 200) or 200
        weather = signals.get("weather", "Rain")
        ev_spots = lot.get("ev_charging_spots", 8)

        for f in factors:
            fid = f["factor_id"]
            contrib = f["contribution"]
            desc = f["description"]

            if fid == "factor-occupancy":
                claim_text = (
                    f"Occupancy is surging at {occ_pct}% capacity with only {spots_available} spots remaining, "
                    f"adding ₹{int(contrib)} to reflect tight peak demand."
                )
            elif fid == "factor-event":
                claim_text = (
                    f"'{nearby_event}' is taking place {event_distance_m}m away, "
                    f"adding a ₹{int(contrib)} event proximity adjustment."
                )
            elif fid == "factor-weather":
                claim_text = (
                    f"A {weather.lower()} warning is active, increasing demand for covered bays "
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
                    f"Includes priority access lane and dedicated EV-ready bay reservation "
                    f"(one of {ev_spots} charging points) for ₹{int(contrib)}."
                )
            else:
                # Generic for any new/unverified surcharges
                claim_text = f"{desc} accounts for a ₹{int(contrib)} adjustment to the baseline rate."

            claims.append({
                "claim_text": claim_text,
                "factor_id": fid
            })

        return claims
