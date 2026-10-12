"""Reproducible Empirical Evaluation Runner for VeriCore™ Hardening.

Runs seeded Monte Carlo scenarios across baselines, VeriCore, and ablations
at multiple sensor drift levels (0%, 10%, 20%, 30%) with realistic phantom factor
classes (registry-rejected, content-false, and control).
Outputs per-seed JSON/CSV and multi-seed summary (mean and range).

Usage:
    python scripts/run_evaluation.py [--scenarios 1000] [--seeds 42 101 2024]
"""

import sys
import os
import json
import csv
import time
import random
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any

# Add backend/src to path
sys.path.insert(0, os.path.abspath("backend/src"))

from veripark.data_sources.parking_lots import PARKING_LOTS_DB, _init_lots
from veripark.evaluation.scenario_evaluator import (
    METHODS,
    DRIFT_LEVELS,
    PHANTOM_CLASSES,
    run_scenario
)

_init_lots()


def evaluate_seed(seed: int, n_scenarios: int) -> List[Dict[str, Any]]:
    """Runs n_scenarios for every method and drift level using a fixed random seed."""
    lot_ids = list(PARKING_LOTS_DB.keys())
    results_list = []

    for method in METHODS:
        for drift in DRIFT_LEVELS:
            rng = random.Random(seed + int(drift * 1000))

            # Scenario metrics accumulators
            class_a_injected = 0
            class_a_caught = 0
            class_b_injected = 0
            class_b_caught = 0

            valid_factors_total = 0
            false_exclusions_total = 0
            drifted_factors_total = 0
            drift_caught_total = 0

            control_scenarios = 0
            control_adjustments = 0
            control_deltas = []

            price_errors = []
            final_gt_truth_count = 0
            final_gt_prop_violations = 0
            checks_list = []
            live_queries_list = []
            costs_list = []
            wall_time_total = 0.0

            for i in range(n_scenarios):
                lot_id = lot_ids[i % len(lot_ids)]
                phantom_class = PHANTOM_CLASSES[i % len(PHANTOM_CLASSES)]
                res = run_scenario(lot_id, method, drift, rng, phantom_class=phantom_class)

                class_a_injected += res["phantom_class_a_injected"]
                class_a_caught += res["phantom_class_a_caught"]
                class_b_injected += res["phantom_class_b_injected"]
                class_b_caught += res["phantom_class_b_caught"]

                valid_factors_total += res["valid_factors_count"]
                false_exclusions_total += res["false_exclusions"]
                drifted_factors_total += res["drifted_factors_count"]
                drift_caught_total += res["drift_caught"]

                price_errors.append(res["price_error"])

                if res["phantom_class"] == "control":
                    control_scenarios += 1
                    if res["was_adjusted"]:
                        control_adjustments += 1
                        control_deltas.append(res["delta"])

                final_gt_truth_count += res["final_gt_truth"]
                final_gt_prop_violations += res["final_gt_proposed_violation"]

                checks_list.append(res["checks_run"])
                live_queries_list.append(res["live_queries_issued"])
                costs_list.append(res["assumed_cost"])
                wall_time_total += res["wall_time"]

            summary = {
                "seed": seed,
                "method": method,
                "drift_level": drift,
                "scenarios": n_scenarios,
                "catch_rate_class_a_registry_rejected": round(class_a_caught / class_a_injected, 4) if class_a_injected else 0.0,
                "catch_rate_class_b_content_false": round(class_b_caught / class_b_injected, 4) if class_b_injected else 0.0,
                "false_exclusion_rate": round(false_exclusions_total / valid_factors_total, 4) if valid_factors_total else 0.0,
                "drift_catch_rate": round(drift_caught_total / drifted_factors_total, 4) if drifted_factors_total else 0.0,
                "mean_abs_price_error": round(sum(price_errors) / len(price_errors), 2),
                "count_final_gt_truth": final_gt_truth_count,
                "final_gt_proposed_violations": final_gt_prop_violations,
                "adjustment_rate_control": round(control_adjustments / control_scenarios, 4) if control_scenarios else 0.0,
                "mean_adjustment_mag_control": round(sum(control_deltas) / len(control_deltas), 2) if control_deltas else 0.0,
                "mean_checks_run": round(sum(checks_list) / len(checks_list), 2),
                "mean_live_queries": round(sum(live_queries_list) / len(live_queries_list), 2),
                "mean_assumed_cost": round(sum(costs_list) / len(costs_list), 3),
                "total_wall_time_s": round(wall_time_total, 3),
            }
            results_list.append(summary)

    return results_list


def main():
    parser = argparse.ArgumentParser(description="VeriCore Empirical Evaluation")
    parser.add_argument("--scenarios", type=int, default=1000, help="Number of scenarios per setting")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 101, 2024], help="Random seeds")
    args = parser.parse_args()

    docs_dir = Path("docs")
    docs_dir.mkdir(parents=True, exist_ok=True)

    all_seed_results = []

    print(f"=== Starting VeriCore Evaluation ({args.scenarios} scenarios/setting across seeds {args.seeds}) ===")

    start_eval = time.time()
    for seed in args.seeds:
        seed_start = time.time()
        seed_data = evaluate_seed(seed, args.scenarios)
        all_seed_results.extend(seed_data)

        # Write per-seed JSON
        json_file = docs_dir / f"eval_results_seed_{seed}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, indent=2)

        # Write per-seed CSV
        csv_file = docs_dir / f"eval_results_seed_{seed}.csv"
        if seed_data:
            keys = list(seed_data[0].keys())
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(seed_data)

        print(f"Seed {seed} completed in {round(time.time() - seed_start, 2)}s -> {json_file}")

    # Compute multi-seed aggregated metrics (mean and range)
    grouped = defaultdict(list)
    for row in all_seed_results:
        key = (row["method"], row["drift_level"])
        grouped[key].append(row)

    metric_keys = [
        "catch_rate_class_a_registry_rejected",
        "catch_rate_class_b_content_false",
        "false_exclusion_rate",
        "drift_catch_rate",
        "mean_abs_price_error",
        "count_final_gt_truth",
        "final_gt_proposed_violations",
        "adjustment_rate_control",
        "mean_adjustment_mag_control",
        "mean_checks_run",
        "mean_live_queries",
        "mean_assumed_cost",
    ]

    multiseed_summary = []
    for (method, drift), rows in grouped.items():
        summary_row = {
            "method": method,
            "drift_level": drift,
            "seeds": args.seeds,
            "scenarios_per_seed": args.scenarios,
        }
        for m in metric_keys:
            vals = [r[m] for r in rows]
            mean_v = sum(vals) / len(vals)
            min_v = min(vals)
            max_v = max(vals)
            summary_row[f"{m}_mean"] = round(mean_v, 3)
            summary_row[f"{m}_range"] = f"[{round(min_v, 3)}, {round(max_v, 3)}]"
        multiseed_summary.append(summary_row)

    # Save multi-seed summary
    summary_json = docs_dir / "eval_summary_multiseed.json"
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(multiseed_summary, f, indent=2)

    summary_csv = docs_dir / "eval_summary_multiseed.csv"
    if multiseed_summary:
        keys = list(multiseed_summary[0].keys())
        with open(summary_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(multiseed_summary)

    print(f"\nMulti-seed summary written -> {summary_json} and {summary_csv}")
    print(f"Total evaluation time: {round(time.time() - start_eval, 2)}s")

    # Print markdown table for quick review
    print("\n" + "="*110)
    print("EMPIRICAL EVALUATION SUMMARY (Multi-Seed Mean; cost in assumed relative units, not measured time)")
    print("="*110)
    header = f"{'Method':<24} | {'Drift':<5} | {'Class A Catch':<13} | {'Class B Catch':<13} | {'Drift Catch':<11} | {'Price Err':<9} | {'Violations':<10} | {'Cost (units)':<12} | {'Live Qs':<7}"
    print(header)
    print("-" * len(header))
    for s in multiseed_summary:
        print(f"{s['method']:<24} | {s['drift_level']:<5.2f} | {s['catch_rate_class_a_registry_rejected_mean']:<13.3f} | {s['catch_rate_class_b_content_false_mean']:<13.3f} | {s['drift_catch_rate_mean']:<11.3f} | {s['mean_abs_price_error_mean']:<9.2f} | {s['final_gt_proposed_violations_mean']:<10} | {s['mean_assumed_cost_mean']:<12.3f} | {s['mean_live_queries_mean']:<7.2f}")


if __name__ == "__main__":
    main()
