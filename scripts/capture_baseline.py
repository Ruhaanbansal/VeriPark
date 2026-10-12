"""STEP 0: Capture baseline metrics for all 8 lots before any hardening changes.

Usage: PYTHONPATH=backend/src python scripts/capture_baseline.py [output_path]
"""
import sys, json, time, os

sys.path.insert(0, os.path.abspath("backend/src"))

from veripark.config import load_settings
from veripark.pipeline import VeriParkPipeline
from veripark.data_sources.parking_lots import PARKING_LOTS_DB, _init_lots

_init_lots()

settings = load_settings()
# Use a temp ledger so we don't pollute the real one
import tempfile, pathlib
tmp = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
tmp.close()

pipeline = VeriParkPipeline(config=settings, ledger_path=tmp.name)

lot_ids = list(PARKING_LOTS_DB.keys())
results = {}

for lot_id in lot_ids:
    dec_id = f"baseline-{lot_id}"
    start = time.perf_counter()
    res = pipeline.process_decision(lot_id, duration_hours=2, decision_id=dec_id)
    elapsed = time.perf_counter() - start

    pricing = res["pricing_result"]
    resum   = res["resummation"]
    verdicts = res["verdicts"]

    claims = []
    for v in verdicts:
        claims.append({
            "factor_id":   v.factor_id,
            "materiality": v.materiality,
            "tier":        v.tier,
            "verdict":     v.verdict,
            "check_detail": v.check_detail,
        })

    results[lot_id] = {
        "lot_name":       res["lot"]["name"],
        "base_price":     pricing["base_price"],
        "proposed_price": pricing["proposed_price"],
        "final_price":    resum["final_price"],
        "delta":          resum["delta"],
        "was_adjusted":   resum["was_adjusted"],
        "excluded_factors": resum["excluded_factors"],
        "claims":         claims,
        "wall_time_s":    round(elapsed, 4),
    }

    assert resum["final_price"] <= pricing["proposed_price"], \
        f"INVARIANT VIOLATED for {lot_id}: final > proposed"

output_path = sys.argv[1] if len(sys.argv) > 1 else "docs/baseline_before.json"
pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

os.unlink(tmp.name)
print(f"Baseline captured for {len(results)} lots -> {output_path}")
print("Invariant final<=proposed: OK for all lots")
for lid, r in results.items():
    adj = "ADJUSTED" if r["was_adjusted"] else "clean"
    print(f"  {lid:<35} base={r['base_price']:6.1f} proposed={r['proposed_price']:6.1f} "
          f"final={r['final_price']:6.1f} delta={r['delta']:5.1f} [{adj}]")
