"""Evaluation harness for VeriPark and the VeriCore™ Assurance Engine.

Calculates aggregate operational metrics derived directly from ledger records:
- decision_adjustment_frequency (Component 3)
- decision_adjustment_magnitude (Component 3)
- verification_cost_reduction_pct (Component 1) via assumed relative cost units
- measured proxies: checks_per_tier and live_queries_issued
- real daily trend aggregation with deduplication (last-wins)
"""

from typing import Dict, Any, List, Optional
from collections import defaultdict
from pathlib import Path
import yaml

from veripark.vericore.ledger import DecisionLedger

CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "settings.yaml"

def load_cost_units() -> Dict[str, float]:
    """Loads relative cost units from settings.yaml (assumed relative units, not measured)."""
    default_units = {"deep": 1.0, "standard": 0.3, "light": 0.05}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                units = cfg.get("vericore", {}).get("evaluation", {}).get("cost_units")
                if units and isinstance(units, dict):
                    return {k: float(v) for k, v in units.items()}
        except Exception:
            pass
    return default_units

class EvaluationHarness:
    def __init__(self, ledger: DecisionLedger):
        self.ledger = ledger
        self.cost_units = load_cost_units()

    def compute_aggregate_metrics(self) -> Dict[str, Any]:
        # Deduplicate by decision_id (last-wins) without rewriting ledger history
        records = self.ledger.get_all_records(deduplicate=True)
        total_decisions = len(records)

        if total_decisions == 0:
            return {
                "total_decisions": 0,
                "adjustment_rate": 0.0,
                "avg_adjustment_amount": 0.0,
                "verification_cost_reduction_pct": 0.0,
                "trend": [],
                "is_sample_data": False,
                "checks_per_tier": {"light": 0, "standard": 0, "deep": 0},
                "live_queries_issued": 0,
                "cost_units_assumed": self.cost_units
            }

        adjusted_count = sum(1 for r in records if r.get("was_adjusted", False))
        adjustment_rate = round(adjusted_count / total_decisions, 3)

        adjustments = [float(r.get("delta", 0.0)) for r in records if r.get("was_adjusted", False)]
        avg_adjustment = round(sum(adjustments) / len(adjustments), 2) if adjustments else 0.0

        # Compute tier checks, live queries, and relative cost savings
        checks_per_tier = {"light": 0, "standard": 0, "deep": 0}
        live_queries_issued = 0

        for r in records:
            verdicts = r.get("evidence_payload", {}).get("verdicts", [])
            for v in verdicts:
                tier = v.get("tier", "standard")
                checks_per_tier[tier] = checks_per_tier.get(tier, 0) + 1
                if tier == "deep":
                    live_queries_issued += 1

        total_claims = sum(checks_per_tier.values())
        if total_claims > 0:
            actual_cost = (
                checks_per_tier.get("deep", 0) * self.cost_units.get("deep", 1.0) +
                checks_per_tier.get("standard", 0) * self.cost_units.get("standard", 0.3) +
                checks_per_tier.get("light", 0) * self.cost_units.get("light", 0.05)
            )
            uniform_deep_cost = float(total_claims) * self.cost_units.get("deep", 1.0)
            savings_pct = round(((uniform_deep_cost - actual_cost) / uniform_deep_cost) * 100.0, 1)
        else:
            savings_pct = 0.0

        # Derive daily buckets from real record timestamps
        day_buckets = defaultdict(list)
        for r in records:
            ts = r.get("timestamp", "")
            if isinstance(ts, str) and len(ts) >= 10:
                day = ts[:10]
                day_buckets[day].append(r)

        trend: List[Dict[str, Any]] = []
        for day in sorted(day_buckets.keys()):
            day_recs = day_buckets[day]
            day_adj = sum(1 for x in day_recs if x.get("was_adjusted", False))
            trend.append({
                "date": day,
                "count": len(day_recs),
                "adjustment_rate": round(day_adj / len(day_recs), 3) if day_recs else 0.0
            })

        return {
            "total_decisions": total_decisions,
            "adjustment_rate": adjustment_rate,
            "avg_adjustment_amount": avg_adjustment,
            "verification_cost_reduction_pct": savings_pct,
            "trend": trend,
            "is_sample_data": False,
            "checks_per_tier": checks_per_tier,
            "live_queries_issued": live_queries_issued,
            "cost_units_assumed": self.cost_units
        }
