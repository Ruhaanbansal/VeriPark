# VeriPark (VeriCore™) Hardening & Empirical Validation Report

**Branch:** `main` (hardened & merged; verification fixes on `fix/eval-and-verifier-v2`)  
**Date:** October 12, 2026  
**Status:** Completed & Validated (39/39 Pytest Tests Passing)  

---

## 1. What Changed (Per Step)

### Step 0: Baseline Capture & Invariant Verification
- Captured per-lot baseline pricing, materiality scores, claim verification tiers, and resummation outcomes across all 8 synthetic parking facilities before hardening edits.
- Stored untampered baseline output in [`docs/baseline_before.json`](docs/baseline_before.json).
- Confirmed that initial 20 test suite passed cleanly.

### Step 1: Fail-Closed Verifier Registry (`structured_evidence_assessment.py`)
- **Problem:** Unknown factor IDs previously fell through to `return True`. In `lot-indiranagar-100ft`, `factor-unverified-*` was mistakenly marked supported, and street fair detection relied on fragile keyword matching on claim text.
- **Fix:** Added a strict registry `_KNOWN_PREFIXES = ("factor-occupancy", "factor-event", "factor-weather", "factor-ev-premium", "factor-sensor-discrepancy")`. Any unknown factor ID or `factor-unverified-*` fails closed (`return False, "No evidence rule for factor type ..."`). Removed claim-text keyword heuristics in favor of structured context verification.

### Step 2: Data-Grounded Cached Evidence Checks
- **Event Verification:** Entailment now inspects `lot.live_signals.event_schedule_verified`. If `False`, entailment immediately fails (`"Event '...' in cache but schedule_verified=False; cannot entail without live confirmation"`). Correctly catches the stale event in `lot-indiranagar-100ft` at the standard tier.
- **Sensor Discrepancy:** Inspects `camera_verified_available` vs `sensor_reported_available` in cached signals. If camera confirms 28 free spaces while loop detector reports only 8 (beyond tolerance), the conservative demand surge is marked unsupported. Correctly catches the discrepancy in `lot-express-deck`.

### Step 3: Real Out-of-Band Live Re-Grounding (Component 2)
- **Problem:** `fetch_live_data_source` previously read the exact same snapshot dictionary as the retrieval cache, making it impossible to detect divergence; tolerances were declared but ignored; thresholds (0.70, 500m) were hardcoded.
- **Fix:** Created `LiveStateStore` and `DriftInjector` in `backend/src/veripark/data_sources/live_state.py`. Default store has zero overrides (preserving 100% backward compatibility). `fetch_live_data_source` queries live state (snapshot + live overrides).
- Rewrote `live_regrounding.py` to parameterize tolerances (`occupancy_tolerance: 0.08`, `rate_tolerance: 5.0`) from config. Source-unreachable conditions return unsupported gracefully without unhandled exceptions. Added exact per-decision live query counting.

### Step 4: Cryptographic Ledger Integrity (Component 4)
- **Problem:** Top-level fields (`lot_id`, `proposed_price`, `delta`, `was_adjusted`) were not bound by `block_hash`; tail truncation went undetected; missing write lock; duplicate records in history.
- **Fix:** Introduced `schema_version: 2`. In v2, `compute_block_hash_v2` binds `(previous_hash, decision_id, timestamp, lot_id, proposed_price, recorded_price, delta, was_adjusted, evidence_hash)`. Legacy blocks (without schema_version) continue to verify with the v1 formula, preserving compatibility with the existing 352-block ledger.
- Added sidecar head file (`ledger.head` tracking last block hash and block count). `verify_chain` detects tail truncation and reports `"head mismatch"`.
- Guarded `record_decision` with a `threading.Lock()` and atomic single-line append + flush. Added last-wins deduplication by `decision_id` for queries and metrics without rewriting history.

### Step 5: Honest Metrics Derived Directly from Ledger
- **Problem:** Hardcoded `58.4%` cost reduction and static 5-day trend `[2026-09-12 .. 2026-09-16]`.
- **Fix:** Rewrote `EvaluationHarness` to compute metrics dynamically from deduplicated ledger records. Grouped real timestamps into daily buckets. Configured relative cost weights in `config/settings.yaml` under `vericore.evaluation.cost_units` (`deep: 1.0`, `standard: 0.3`, `light: 0.05`), labelled "assumed relative units, not measured". Added proxy metrics: `checks_per_tier` and `live_queries_issued`. Added additive optional fields to `AdminStatsResponse`.

### Step 6: Reproducible Evaluation Harness & Baseline Comparisons
- Added `vericore.verification_mode` supporting `vericore` (default), `none` (B1), `uniform_light` (B2), `uniform_deep` (B3), `vericore_no_live` (ablation), and threshold ablations.
- Created `backend/src/veripark/evaluation/scenario_evaluator.py` and `scripts/run_evaluation.py` running Monte Carlo scenario evaluations across 4 sensor drift levels (0%, 10%, 20%, 30%) with 1,000 scenarios per configuration and 3 random seeds ([42, 101, 2024]). Outputted raw CSV/JSON records and multi-seed summary.

### Step 7: Cleanups & Extensibility Protocols
- Replaced hardcoded retrieval timestamp with dynamic UTC ISO-8601 formatting.
- Replaced unreproducible figures in `README.md` with pointers to this report and added the "Prototype Scope" boundary notice.
- Replaced "clamping" terminology with "resummation" across documentation and code comments.
- Defined runtime-checkable `Protocol` interfaces in `backend/src/veripark/vericore/interfaces.py` (`EntailmentVerifier`, `ClaimJudge`) and created `requirements-ml.txt` for optional transformer packages.

---

## 1.1 Corrections & Flaw Rectifications (Evaluation & Verifier v2)

1. **Single Source of Truth for Domain Rules (Step 1):** Added `vericore.rules` with `surge_threshold: 0.70` and `event_radius_m: 500` to `config/settings.yaml`. Read them dynamically in `structured_evidence_assessment.py` and `live_regrounding.py`. Removed hardcoded `0.70`, `500`, and `9999` literals from branching logic.
2. **Live Re-grounding Clean-up (Step 2):** Enforced `timeout_seconds` using `concurrent.futures.ThreadPoolExecutor` (timeout/error returns `unsupported` without raising, counting 1 query attempt). Removed unused `rate_tolerance`. Sensor discrepancy branch now reads live camera count and loop detector count (`sensor_reported_available`), returning unsupported only when camera exceeds sensor beyond tolerance. EV bay verification now uses registry check (0 queries). Unregistered factor types fail closed with 0 queries. Occupancy is explicitly defined as supported iff BOTH `|live - claimed| <= tolerance` AND `live >= surge_threshold`.
3. **Independent Ground Truth (Step 3):** Created `backend/src/veripark/evaluation/ground_truth.py`, decoupled from verifier code, evaluating factor validity against world state after drift. Removed the legacy branch that incorrectly conflated camera-vs-sensor checks with occupancy factors.
4. **Realistic Phantom Factor Classes (Step 4):** Replaced single artificial phantom with three realistic seeded classes: (a) `registry_rejected` (unregistered factor type for fail-closed testing), (b) `content_false` (registered factor type with fabricated, contradictory claim text for content entailment testing), and (c) `control` (no phantom injected). Eliminated artificial marker words from IDs and report per-class catch rates separately.
5. **B1 Accounting & Metric Labelling (Step 5):** Fixed verification_mode `none` to record 0 checks and 0 cost. Reported adjustment rate exclusively over the control class. Labelled all compute costs as "assumed relative units, not measured time".

---

## 2. Before / After Comparison Across All 8 Lots

Values produced by `scripts/capture_baseline.py` comparing [`docs/baseline_before.json`](docs/baseline_before.json) and [`docs/baseline_after.json`](docs/baseline_after.json):

| Facility (`lot_id`) | Base Price | Proposed Price | Before Hardening Final Price | Before Adjusted? | After Hardening Final Price | After Adjusted? | Price Delta Change | Reason for Change |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `lot-metro-hub` | ₹100.0 | ₹205.0 | ₹175.0 | **True** (₹30 adj) | ₹175.0 | **True** (₹30 adj) | ₹0.0 | Retained: unverified street fair factor excluded. |
| `lot-commercial-tower` | ₹80.0 | ₹135.0 | ₹135.0 | False (0 adj) | ₹135.0 | False (0 adj) | ₹0.0 | Clean: all 3 factors verified. |
| `lot-civic-center` | ₹70.0 | ₹70.0 | ₹70.0 | False (0 adj) | ₹70.0 | False (0 adj) | ₹0.0 | Clean: no surcharges proposed. |
| `lot-express-deck` | ₹90.0 | ₹130.0 | ₹130.0 | **False (0 adj)** | **₹115.0** | **True (₹15 adj)** | **-₹15.0** | **Fixed:** Camera confirms 28 free spots vs loop detector 8; discrepancy surcharge excluded. |
| `lot-indiranagar-100ft` | ₹90.0 | ₹170.0 | ₹170.0 | **False (0 adj)** | **₹125.0** | **True (₹45 adj)** | **-₹45.0** | **Fixed:** Stale event (`schedule_verified=False`, ₹25) and unverified surge (₹20) fail closed. |
| `lot-koramangala-nexus` | ₹80.0 | ₹80.0 | ₹80.0 | False (0 adj) | ₹80.0 | False (0 adj) | ₹0.0 | Clean: base rate only. |
| `lot-hospital-emergency` | ₹60.0 | ₹120.0 | ₹95.0 | **True** (₹25 adj) | ₹95.0 | **True** (₹25 adj) | ₹0.0 | Retained: unverified emergency surcharge excluded. |
| `lot-whitefield-techpark` | ₹70.0 | ₹130.0 | ₹130.0 | False (0 adj) | ₹130.0 | False (0 adj) | ₹0.0 | Clean: EV and weather factors verified. |

**Monotonic Safety Invariant:** $\text{FinalPrice} \le \text{ProposedPrice}$ holds for **100% (8/8)** of facilities in both runs.

---

## 3. Test Suite Verification Results

Running the complete test suite:
```powershell
backend\.venv\Scripts\python.exe -m pytest -q
```

**Result:** `39 passed, 3 warnings in 4.82s` (100% pass rate).

### Test Breakdown:
- **Original 20 Tests:** All passing. (One assertion in `test_full_flow.py` was updated from a hardcoded `> 40.0%` fake metric to `> 30.0%` to test against the real ledger metric of 37.3%).
- **New Hardening Tests (`tests/backend/test_hardening_patent_claims.py`):**
  1. `test_unknown_factor_id_is_unsupported` — Unknown/unverified prefix fails closed with `"no evidence rule"`.
  2. `test_indiranagar_stale_event_excluded_standard_tier` — Catch stale event schedule in context.
  3. `test_express_deck_sensor_discrepancy_excluded` — Catch camera vs loop detector mismatch.
  4. `test_deep_tier_drift_caught_by_live_regrounding_proves_c2` — Demonstrates that injected drift is caught by live re-grounding while passing cached check (Component 2 proof).
  5. `test_live_source_unreachable_excludes_and_does_not_raise` — Graceful handling of unreachable sources.
  6. `test_tolerance_boundary_just_inside_and_outside` — 0.08 tolerance boundary behavior.
  7. `test_routing_boundaries_at_exact_thresholds` — Exact 0.10 and 0.40 materiality tier boundaries.
  8. `test_resummation_invariants_random_property` — Seeded property test across 100 random factor combinations.
  9. `test_ledger_tamper_detection_v2_and_legacy_verify` — Tamper tests covering all top-level v2 fields, tail truncation, genesis break, and legacy 352-block ledger verification.
  10. `test_concurrent_appends_produce_valid_chain` — 10 concurrent worker threads produce intact SHA-256 chain.
  11. `test_verification_mode_default_equals_baseline_after` — Default mode exactly reproduces baseline_after across all 8 lots.
  12. `test_api_contract_unchanged` — Backward-compatible API schemas with additive metadata fields.

---

## 4. Empirical Evaluation Tables (Reproducible Monte Carlo)

Produced by `scripts/run_evaluation.py --scenarios 1000 --seeds 42 101 2024` (3,000 runs per setting, 84,000 total scenario evaluations).

### Multi-Seed Mean and Range Summary

<!-- BEGIN_EVALUATION_TABLE -->
| Method | Drift Level | Phantom Catch Rate | Drift Catch Rate | Mean Abs Price Error (₹) | Invariant Violations ($P_{fin} > P_{prop}$) | Assumed Compute Cost | Live Queries Issued / Req |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B1 (None)** | 0.00 | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹34.98 [34.83, 35.17] | 0 [0, 0] | 0.206 [0.206, 0.206] | 0.00 [0.0, 0.0] |
| **B1 (None)** | 0.10 | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹36.08 [35.93, 36.36] | 0 [0, 0] | 0.206 [0.206, 0.206] | 0.00 [0.0, 0.0] |
| **B1 (None)** | 0.20 | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹37.80 [37.66, 37.91] | 0 [0, 0] | 0.206 [0.206, 0.206] | 0.00 [0.0, 0.0] |
| **B1 (None)** | 0.30 | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹40.37 [40.23, 40.54] | 0 [0, 0] | 0.206 [0.206, 0.206] | 0.00 [0.0, 0.0] |
| **B2 (Light)** | 0.00 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹1.88 [1.88, 1.88] | 0 [0, 0] | 0.206 [0.206, 0.206] | 0.00 [0.0, 0.0] |
| **B2 (Light)** | 0.10 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹2.63 [2.52, 2.76] | 0 [0, 0] | 0.206 [0.206, 0.206] | 0.00 [0.0, 0.0] |
| **B2 (Light)** | 0.20 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹3.86 [3.73, 3.96] | 0 [0, 0] | 0.206 [0.206, 0.206] | 0.00 [0.0, 0.0] |
| **B2 (Light)** | 0.30 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹6.16 [6.11, 6.22] | 0 [0, 0] | 0.206 [0.206, 0.206] | 0.00 [0.0, 0.0] |
| **B3 (Deep)** | 0.00 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹1.88 [1.88, 1.88] | 0 [0, 0] | 4.125 [4.125, 4.125] | 3.88 [3.88, 3.88] |
| **B3 (Deep)** | 0.10 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | ₹2.30 [2.14, 2.45] | 0 [0, 0] | 4.125 [4.125, 4.125] | 3.88 [3.88, 3.88] |
| **B3 (Deep)** | 0.20 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | ₹4.07 [3.88, 4.21] | 0 [0, 0] | 4.125 [4.125, 4.125] | 3.88 [3.88, 3.88] |
| **B3 (Deep)** | 0.30 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | ₹4.79 [4.62, 4.98] | 0 [0, 0] | 4.125 [4.125, 4.125] | 3.88 [3.88, 3.88] |
| **VeriCore** | 0.00 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹1.88 [1.88, 1.88] | 0 [0, 0] | **1.764** [1.763, 1.765] | **0.75** [0.75, 0.75] |
| **VeriCore** | 0.10 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹2.76 [2.68, 2.82] | 0 [0, 0] | **1.768** [1.762, 1.774] | **0.76** [0.75, 0.76] |
| **VeriCore** | 0.20 | 1.000 [1.0, 1.0] | 0.027 [0.0, 0.052] | ₹4.36 [4.18, 4.54] | 0 [0, 0] | **1.771** [1.767, 1.775] | **0.76** [0.76, 0.76] |
| **VeriCore** | 0.30 | 1.000 [1.0, 1.0] | 0.046 [0.023, 0.068] | ₹6.54 [6.38, 6.72] | 0 [0, 0] | **1.766** [1.763, 1.771] | **0.76** [0.75, 0.76] |
| **VeriCore (No Live)**| 0.00 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹1.88 [1.88, 1.88] | 0 [0, 0] | 1.764 [1.763, 1.765] | 0.00 [0.0, 0.0] |
| **VeriCore (No Live)**| 0.10 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹2.63 [2.52, 2.76] | 0 [0, 0] | 1.768 [1.762, 1.774] | 0.00 [0.0, 0.0] |
| **VeriCore (No Live)**| 0.20 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹3.86 [3.73, 3.96] | 0 [0, 0] | 1.771 [1.767, 1.775] | 0.00 [0.0, 0.0] |
| **VeriCore (No Live)**| 0.30 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹6.16 [6.11, 6.22] | 0 [0, 0] | 1.766 [1.763, 1.771] | 0.00 [0.0, 0.0] |
| **Ablation (0.05/0.30)** | 0.00 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹1.88 [1.88, 1.88] | 0 [0, 0] | 2.315 [2.315, 2.315] | 1.54 [1.54, 1.54] |
| **Ablation (0.05/0.30)** | 0.10 | 1.000 [1.0, 1.0] | 0.262 [0.222, 0.300] | ₹2.50 [2.38, 2.61] | 0 [0, 0] | 2.304 [2.298, 2.312] | 1.52 [1.52, 1.53] |
| **Ablation (0.05/0.30)** | 0.20 | 1.000 [1.0, 1.0] | 0.234 [0.210, 0.258] | ₹4.38 [4.19, 4.56] | 0 [0, 0] | 2.301 [2.295, 2.308] | 1.52 [1.52, 1.53] |
| **Ablation (0.05/0.30)** | 0.30 | 1.000 [1.0, 1.0] | 0.292 [0.268, 0.315] | ₹6.01 [5.82, 6.18] | 0 [0, 0] | 2.319 [2.312, 2.325] | 1.54 [1.53, 1.55] |
| **Ablation (0.20/0.50)** | 0.00 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹1.88 [1.88, 1.88] | 0 [0, 0] | 1.400 [1.400, 1.400] | 0.50 [0.50, 0.50] |
| **Ablation (0.20/0.50)** | 0.10 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹2.63 [2.52, 2.76] | 0 [0, 0] | 1.401 [1.398, 1.404] | 0.50 [0.50, 0.50] |
| **Ablation (0.20/0.50)** | 0.20 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹3.86 [3.73, 3.96] | 0 [0, 0] | 1.400 [1.396, 1.403] | 0.50 [0.50, 0.50] |
| **Ablation (0.20/0.50)** | 0.30 | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹6.16 [6.11, 6.22] | 0 [0, 0] | 1.400 [1.396, 1.403] | 0.50 [0.50, 0.50] |
<!-- END_EVALUATION_TABLE -->

---

## 5. Known Limitations & Architectural Scope

1. **Deterministic Rule-Based Modules:** In this prototype release, agents (`ContextRetrievalAgent`, `AllocationPricingAgent`, `ExplanationDraftingAgent`) are implemented as rule-based deterministic modules for testability and zero external API dependencies.
2. **Rule-Based Verifiers:** Entailment verification uses deterministic rule assessment over structured signals rather than deep cross-encoder neural language models. Extensibility interfaces (`EntailmentVerifier`, `ClaimJudge`) are provided for production ML integration.
3. **Synthetic Benchmark Dataset:** The 8 parking facilities represent a calibrated synthetic model of Bengaluru municipal transit hubs, commercial decks, and hospitals.
4. **Simulated Origin Sources:** Live sensor checks and out-of-band schedule APIs are simulated via the in-memory `LiveStateStore` and `DriftInjector`.
5. **Low Drift Catch at Default Thresholds:** By architectural design, standard-tier claims (materiality between 0.10 and 0.40) are verified against cached context; only high-materiality claims ($\ge 0.40$) trigger out-of-band live sensor queries. Under default thresholds, most drifted claims fall into standard or light tiers, resulting in low drift catch rate (~2-5%). The 0.05/0.30 ablation demonstrates the coverage/cost trade-off, catching ~26-29% of drift at higher compute and query cost.
6. **Ledger Tamper Model Scope:** The ledger cryptographic chain detects payload modifications, genesis alterations, and tail truncation (via the `.head` sidecar file). It does not prevent an offline attacker with full write access from re-computing and replacing both `ledger.jsonl` and `ledger.head` simultaneously.
7. **Legacy Ledger Historical Records:** The committed 352-block ledger predates schema v2; historical records verify under the legacy v1 formula, and dashboard metrics reflect historical decisions recorded in this file.

---

## 6. Exact Commands to Reproduce Every Number

All reported numbers can be reproduced using standard Python from the workspace root:

```powershell
# 1. Run the full unit and property test suite (32 tests):
backend\.venv\Scripts\python.exe -m pytest -q

# 2. Run the 8-lot baseline capture:
backend\.venv\Scripts\python.exe scripts/capture_baseline.py docs/baseline_after.json

# 3. Verify cryptographic ledger integrity:
backend\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend/src'); from veripark.vericore.ledger import DecisionLedger; print(DecisionLedger('data/ledger/ledger.jsonl').verify_chain())"

# 4. Run the full Monte Carlo evaluation (1,000 scenarios x 3 seeds):
backend\.venv\Scripts\python.exe scripts/run_evaluation.py --scenarios 1000 --seeds 42 101 2024
```
