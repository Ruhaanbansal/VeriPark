"""Render Markdown Tables for Documentation from Multi-Seed Evaluation Summary.

Reads docs/eval_summary_multiseed.json and writes generated markdown tables
into docs/HARDENING_REPORT.md and README.md between dedicated marker comments.
"""

import json
from pathlib import Path


def render_markdown_tables():
    docs_dir = Path("docs")
    summary_path = docs_dir / "eval_summary_multiseed.json"

    if not summary_path.exists():
        raise FileNotFoundError(f"Missing evaluation summary: {summary_path}")

    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Render Comprehensive Table for HARDENING_REPORT.md
    report_rows = []
    report_rows.append(
        "| Method | Drift Level | Class A Catch (Registry) | Class B Catch (Content) | Drift Catch Rate | False Exclusion Rate | Mean Abs Price Error (₹) | Invariant Violations ($P_{fin} > P_{prop}$) | Assumed Compute Cost* | Live Queries Issued / Req |"
    )
    report_rows.append(
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    )

    # Helper method label formatter
    label_map = {
        "B1_none": "**B1 (None)**",
        "B2_uniform_light": "**B2 (Light)**",
        "B3_uniform_deep": "**B3 (Deep)**",
        "VeriCore": "**VeriCore**",
        "VeriCore_no_live": "**VeriCore (No Live)**",
        "Ablation_thresh_05_30": "**Ablation (0.05/0.30)**",
        "Ablation_thresh_20_50": "**Ablation (0.20/0.50)**",
    }

    for row in data:
        method_label = label_map.get(row["method"], row["method"])
        drift_str = f"{row['drift_level']:.2f}"
        class_a_str = f"{row['catch_rate_class_a_registry_rejected_mean']:.3f} {row['catch_rate_class_a_registry_rejected_range']}"
        class_b_str = f"{row['catch_rate_class_b_content_false_mean']:.3f} {row['catch_rate_class_b_content_false_range']}"
        drift_str_rate = f"{row['drift_catch_rate_mean']:.3f} {row['drift_catch_rate_range']}"
        false_excl_str = f"{row['false_exclusion_rate_mean']:.3f} {row['false_exclusion_rate_range']}"
        err_str = f"₹{row['mean_abs_price_error_mean']:.2f} {row['mean_abs_price_error_range']}"
        viols_str = f"{row['final_gt_proposed_violations_mean']} {row['final_gt_proposed_violations_range']}"
        cost_str = f"{row['mean_assumed_cost_mean']:.3f} {row['mean_assumed_cost_range']}"
        queries_str = f"{row['mean_live_queries_mean']:.2f} {row['mean_live_queries_range']}"

        report_rows.append(
            f"| {method_label} | {drift_str} | {class_a_str} | {class_b_str} | {drift_str_rate} | {false_excl_str} | {err_str} | {viols_str} | {cost_str} | {queries_str} |"
        )

    report_table_md = "\n".join(report_rows) + "\n\n*\\*Assumed relative units, not measured time.*"

    # 2. Render Key Findings Summary Table for README.md (at 0% drift)
    by_method_0drift = {}
    for row in data:
        if row["drift_level"] == 0.0:
            by_method_0drift[row["method"]] = row

    b1 = by_method_0drift.get("B1_none", {})
    b2 = by_method_0drift.get("B2_uniform_light", {})
    b3 = by_method_0drift.get("B3_uniform_deep", {})
    vc = by_method_0drift.get("VeriCore", {})

    readme_rows = [
        "| Metric | Baseline B1 (None) | Baseline B2 (Light) | Baseline B3 (Deep) | VeriCore (Adaptive) |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| **Class A Catch (Registry-Rejected)** | {b1.get('catch_rate_class_a_registry_rejected_mean', 0.0):.1%} | {b2.get('catch_rate_class_a_registry_rejected_mean', 0.0):.1%} | {b3.get('catch_rate_class_a_registry_rejected_mean', 0.0):.1%} | **{vc.get('catch_rate_class_a_registry_rejected_mean', 0.0):.1%}** |",
        f"| **Class B Catch (Content-False)** | {b1.get('catch_rate_class_b_content_false_mean', 0.0):.1%} | {b2.get('catch_rate_class_b_content_false_mean', 0.0):.1%} | {b3.get('catch_rate_class_b_content_false_mean', 0.0):.1%} | **{vc.get('catch_rate_class_b_content_false_mean', 0.0):.1%}** |",
        f"| **Monotonic Invariant Violations** | {int(b1.get('final_gt_proposed_violations_mean', 0))} | {int(b2.get('final_gt_proposed_violations_mean', 0))} | {int(b3.get('final_gt_proposed_violations_mean', 0))} | **{int(vc.get('final_gt_proposed_violations_mean', 0))} ($P_{{final}} \\le P_{{prop}}$ holds in all runs)** |",
        f"| **Assumed Compute Cost (relative units)** | {b1.get('mean_assumed_cost_mean', 0.0):.3f} units | {b2.get('mean_assumed_cost_mean', 0.0):.3f} units | {b3.get('mean_assumed_cost_mean', 0.0):.3f} units | **{vc.get('mean_assumed_cost_mean', 0.0):.3f} units** |",
        f"| **Live Origin Queries Issued / Req** | {b1.get('mean_live_queries_mean', 0.0):.2f} | {b2.get('mean_live_queries_mean', 0.0):.2f} | {b3.get('mean_live_queries_mean', 0.0):.2f} / req | **{vc.get('mean_live_queries_mean', 0.0):.2f} / req** |",
        f"| **Mean Absolute Price Error (0% drift)** | ₹{b1.get('mean_abs_price_error_mean', 0.0):.2f} | ₹{b2.get('mean_abs_price_error_mean', 0.0):.2f} | ₹{b3.get('mean_abs_price_error_mean', 0.0):.2f} | **₹{vc.get('mean_abs_price_error_mean', 0.0):.2f}** |",
        f"| **False Exclusion Rate (Valid Factors)** | {b1.get('false_exclusion_rate_mean', 0.0):.1%} | {b2.get('false_exclusion_rate_mean', 0.0):.1%} | {b3.get('false_exclusion_rate_mean', 0.0):.1%} | **{vc.get('false_exclusion_rate_mean', 0.0):.1%}** |",
    ]
    readme_table_md = "\n".join(readme_rows) + "\n\n*\\*Cost is reported in assumed relative units, not measured time.*"

    # 3. Update docs/HARDENING_REPORT.md between markers
    report_file = Path("docs/HARDENING_REPORT.md")
    if report_file.exists():
        content = report_file.read_text(encoding="utf-8")
        start_marker = "<!-- BEGIN_EVALUATION_TABLE -->"
        end_marker = "<!-- END_EVALUATION_TABLE -->"
        if start_marker in content and end_marker in content:
            pre = content.split(start_marker)[0] + start_marker + "\n\n"
            post = "\n\n" + end_marker + content.split(end_marker)[1]
            report_file.write_text(pre + report_table_md + post, encoding="utf-8")
            print(f"Updated table in {report_file}")
        else:
            print(f"Warning: Markers {start_marker} / {end_marker} not found in {report_file}")

    # 4. Update README.md between markers
    readme_file = Path("README.md")
    if readme_file.exists():
        content = readme_file.read_text(encoding="utf-8")
        start_marker = "<!-- BEGIN_KEY_FINDINGS_TABLE -->"
        end_marker = "<!-- END_KEY_FINDINGS_TABLE -->"
        if start_marker in content and end_marker in content:
            pre = content.split(start_marker)[0] + start_marker + "\n\n"
            post = "\n\n" + end_marker + content.split(end_marker)[1]
            readme_file.write_text(pre + readme_table_md + post, encoding="utf-8")
            print(f"Updated table in {readme_file}")
        else:
            print(f"Warning: Markers {start_marker} / {end_marker} not found in {readme_file}")


if __name__ == "__main__":
    render_markdown_tables()
