from typing import Dict, Any, List
from veripark.api.schemas import PricingResult, PricingFactor

class AllocationPricingAgent:
    """Stage 2: Proposes a recommended parking lot and pricing with decomposed factors.

    Required output contract:
    {
      "recommended_lot_id": str,
      "base_price": float,
      "factors": [{"factor_id": str, "description": str, "contribution": float}, ...],
      "proposed_price": float,
    }
    """

    def propose_pricing(self, lot_context: Dict[str, Any]) -> Dict[str, Any]:
        lot = lot_context["lot"]
        duration_hours = lot_context.get("duration_hours", 2)
        base_rate = lot.get("base_rate_per_hour", 40.0)
        base_price = float(base_rate * duration_hours)

        signals = lot.get("live_signals", {})
        factors: List[Dict[str, Any]] = []

        # 1. Occupancy factor
        occ = signals.get("occupancy_rate", 0.5)
        if occ >= 0.85:
            factors.append({
                "factor_id": "factor-occupancy",
                "description": f"High occupancy surge (over {int(occ*100)}% capacity)",
                "contribution": 35.0
            })
        elif occ >= 0.70:
            factors.append({
                "factor_id": "factor-occupancy",
                "description": f"Moderate demand adjustment ({int(occ*100)}% capacity)",
                "contribution": 20.0
            })

        # 2. Event proximity factor
        if signals.get("nearby_event"):
            factors.append({
                "factor_id": "factor-event",
                "description": f"Surge for nearby event ({signals['nearby_event']})",
                "contribution": 25.0
            })

        # 3. Weather adjustment
        if "Rain" in str(signals.get("weather", "")):
            factors.append({
                "factor_id": "factor-weather",
                "description": "Covered protection premium during heavy rain alert",
                "contribution": 15.0
            })

        # 4. Unverified / hallucinated surcharge from the pricing model
        if signals.get("unverified_surcharge_flag"):
            surcharge_name = signals.get("unverified_surcharge_name", "Special zone surcharge")
            surcharge_amount = float(signals.get("unverified_surcharge_amount", 25.0))
            factors.append({
                "factor_id": f"factor-unverified-{lot['id']}",
                "description": surcharge_name,
                "contribution": surcharge_amount
            })

        # 5. Sensor disparity — camera vs loop-detector mismatch
        if signals.get("sensor_discrepancy_flag"):
            factors.append({
                "factor_id": "factor-sensor-discrepancy",
                "description": "Occupancy sensor vs camera vision count mismatch — applying conservative higher demand estimate",
                "contribution": 15.0
            })

        # 6. EV premium for automated stacks
        if lot.get("lot_type") == "automated_robotic_stack" and not signals.get("unverified_surcharge_flag"):
            factors.append({
                "factor_id": "factor-ev-premium",
                "description": "Priority EV charging bay reservation fee",
                "contribution": 10.0
            })

        sum_contributions = sum(f["contribution"] for f in factors)
        proposed_price = base_price + sum_contributions

        return {
            "recommended_lot_id": lot["id"],
            "base_price": base_price,
            "factors": factors,
            "proposed_price": proposed_price
        }
