# VeriPark (VeriCore™) Evaluation & Verifier Hardening Report (v2)

**Branch:** `fix/eval-and-verifier-v2`  
**Date:** October 13, 2026  
**Status:** Completed, Verified & Reproducible (39/39 Pytest Tests Passing)  
**Evaluator Run:** 1,000 scenarios per configuration across 3 seeds (`[42, 101, 2024]`), total 84,000 scenario evaluations.

---

## 1. What Changed Per Step

### Step 0: Baseline Capture & Verification
- Ran full test suite to establish pre-fix baseline: 32 tests passed cleanly.
- Preserved `docs/eval_summary_multiseed.json` as `docs/eval_summary_before_fix.json` as the immutable historical record before fixes.

### Step 1: Single Source of Truth for Domain Rules
- **Problem:** Verification and evaluation modules duplicated domain constants (`0.70` surge threshold, `500` meter event radius, `9999` distance fallbacks) as magic numbers in branching logic.
- **Fix:** Added `vericore.rules` with `surge_threshold: 0.70` and `event_radius_m: 500` to `config/settings.yaml` and parsed them into `VeriCoreSettings` in `backend/src/veripark/config.py`. Updated `structured_evidence_assessment.py` and `live_regrounding.py` to read rules from config with graceful defaults. Removed hardcoded `0.70`, `500`, and `9999` literals from verifier branching logic. Pricing agent's own internal thresholds were left untouched.

### Step 2: Live Re-Grounding Clean-Up (`live_regrounding.py`)
- **Timeout Enforcement:** Wrapped live source queries in `concurrent.futures.ThreadPoolExecutor` with `future.result(timeout=timeout_seconds)`. On timeout or unexpected exception, verdict returns `"unsupported"` with detail `"live source unavailable/timeout"` without raising, counting 1 query attempt.
- **Removal of Dead Parameters:** Removed unused `rate_tolerance` from configuration schemas, YAML settings, and code paths. Updated docstrings to be strictly truthful.
- **Sensor Discrepancy Verification:** Updated `fetch_live_data_source` and `parking_lots.py` to provide both `camera_verified_available` and `sensor_reported_available`. In `live_regrounding.py`, the sensor discrepancy branch compares live camera count against loop detector count. Returns unsupported only when camera exceeds sensor beyond tolerance (`camera_free - sensor_free > 5`); otherwise supported.
- **Registry Checks for EV Bays:** EV bay verification now queries the lot registry directly (`lot.has_ev_charging`) with detail `"registry check, not a live sensor"`, incurring 0 live queries.
- **Fail-Closed for Unregistered Live Sources:** Types without registered live sources (unregistered IDs, emergency, festival) return unsupported with detail `"no live source registered for this factor type"`, issuing 0 queries. Removed fictional "municipal registry confirmed" message.
- **Occupancy Live Specification:** Explicitly defined occupancy as supported iff BOTH `|live - claimed| <= occupancy_tolerance` AND `live >= surge_threshold`.

### Step 3: Independent Ground Truth Engine (`scenario_evaluator.py`)
- **Problem:** The evaluator previously reused partial verifier code and applied a camera-vs-loop-detector check to occupancy factors, causing valid factors to be classified as invalid (7.7% false exclusions at 0% drift).
- **Fix:** Created `backend/src/veripark/evaluation/ground_truth.py`, completely independent from verifier code. Evaluates factor validity strictly against the post-drift world state:
  - Occupancy valid iff `|live - claimed| <= occupancy_tolerance` AND `live >= surge_threshold`.
  - Event valid iff event exists in live state, `schedule_verified == True`, and `distance_m <= event_radius_m`.
  - Weather valid iff live weather condition contains `"Rain"`.
  - EV premium valid iff lot has EV bays in registry.
  - Sensor discrepancy valid iff `camera <= sensor` beyond tolerance would not be violated (invalid when camera free count exceeds sensor count).
  - Unregistered or phantom factors are strictly invalid.
  - Removed incorrect camera-vs-sensor check from occupancy factors.

### Step 4: Realistic Seeded Phantom Factors
- **Problem:** A single artificial phantom ID (`factor-unverified-phantom-N`) allowed verifiers to catch phantoms by simple substring matching on the word `unverified`.
- **Fix:** Replaced the artificial phantom with three seeded classes:
  - **Class (a) `registry_rejected`:** Unregistered factor type (`factor-vip-concierge`, `factor-express-lane`, etc.) without forbidden marker words, validating fail-closed design property.
  - **Class (b) `content_false`:** Registered factor type (`factor-event`, `factor-occupancy`, `factor-weather`) with fabricated claim text contradicted by ground truth (e.g. marathon on an IPL lot, 85% occupancy claim on a 30% lot), proving detection by semantic content.
  - **Class (c) `control`:** Scenarios with no phantom, enabling clean measurement of baseline adjustment rate, false exclusions, and price error.
- Reported catch rates per class separately.

### Step 5: B1 Accounting & Honest Metric Labelling
- **B1 Accounting:** In `faithfulness_scoring.py`, when `verification_mode == "none"`, checks are not incremented in `checks_per_tier`, correctly reporting 0 checks run and 0.000 compute cost.
- **Metric Scoping:** Adjustment rate is computed strictly over the control class. False-exclusion rate is evaluated across valid factors in all classes. All compute costs are explicitly labelled as "assumed relative units, not measured time". Live queries issued and checks run are reported alongside costs.

---

## 2. Before / After Comparison Table

The following table compares `docs/eval_summary_before_fix.json` (pre-fix baseline) against `docs/eval_summary_multiseed.json` (hardened evaluation) across all key configurations (averaged across seeds 42, 101, 2024):

| Method & Drift Level | Metric | Before Fix | After Fix | Explanation of Change |
| :--- | :--- | :--- | :--- | :--- |
| **B1 (None)** (drift 0.0) | Assumed Compute Cost | 0.206 units | **0.000 units** | Fixed B1 accounting: mode `none` now records 0 checks and 0 cost. |
| **B1 (None)** (drift 0.0) | Mean Abs Price Error | ₹34.98 | **₹27.50** | Evaluator ground truth now accounts for realistic phantom classes. |
| **B2 (Light)** (drift 0.0) | False Exclusion Rate | 7.7% | **0.0%** | Decoupled ground truth eliminated spurious camera-check misapplied to occupancy. |
| **B2 (Light)** (drift 0.0) | Mean Abs Price Error | ₹1.88 | **₹0.00** | Zero false exclusions at 0% drift results in perfect price agreement with ground truth. |
| **B2 (Light)** (drift 0.0) | Assumed Compute Cost | 0.206 units | **0.173 units** | Realistic phantom distribution altered average factors checked per scenario. |
| **B3 (Deep)** (drift 0.0) | False Exclusion Rate | 7.7% | **0.0%** | Decoupled ground truth eliminated spurious camera-check misapplied to occupancy. |
| **B3 (Deep)** (drift 0.0) | Mean Abs Price Error | ₹1.88 | **₹0.00** | Zero false exclusions at 0% drift results in perfect price agreement with ground truth. |
| **B3 (Deep)** (drift 0.0) | Live Queries Issued | 3.88 / req | **2.17 / req** | EV bays now checked via registry (0 queries); unregistered factors fail closed (0 queries). |
| **B3 (Deep)** (drift 0.0) | Assumed Compute Cost | 4.125 units | **3.457 units** | Fewer redundant live queries reduced assumed deep-tier compute units. |
| **VeriCore** (drift 0.0) | False Exclusion Rate | 7.7% | **0.0%** | Verifier and ground truth now strictly agree on domain rules at 0% drift. |
| **VeriCore** (drift 0.0) | Mean Abs Price Error | ₹1.88 | **₹0.00** | Zero false exclusions at 0% drift yields exact ground-truth pricing. |
| **VeriCore** (drift 0.0) | Live Queries Issued | 0.75 / req | **0.52 / req** | EV bay registry check (0 queries) and clean fail-closed paths reduced query load. |
| **VeriCore** (drift 0.0) | Assumed Compute Cost | 1.764 units | **1.570 units** | Materiality routing queries fewer live sources due to EV registry resolution. |
| **VeriCore** (drift 0.1) | Drift Catch Rate | 0.0% | **18.3%** | Fixed sensor-discrepancy branch in live re-grounding now catches sensor drift. |
| **VeriCore** (drift 0.1) | Mean Abs Price Error | ₹2.76 | **₹1.34** | Increased drift catch rate reduced pricing error against true ground truth. |
| **VeriCore** (drift 0.2) | Drift Catch Rate | 2.7% | **22.9%** | Live sensor discrepancy evaluation catches camera-vs-loop drift at high materiality. |
| **VeriCore** (drift 0.2) | Mean Abs Price Error | ₹4.36 | **₹3.31** | Improved drift detection lowers price error across drifted scenarios. |
| **VeriCore** (drift 0.3) | Drift Catch Rate | 4.6% | **25.5%** | Correct sensor-discrepancy comparison catches 25.5% of drifted high-materiality factors. |
| **VeriCore** (drift 0.3) | Mean Abs Price Error | ₹6.54 | **₹5.64** | Resummation excludes caught drifted factors, reducing over-pricing error. |
| **All Methods** (all drift) | Monotonic Violations ($P_{fin} > P_{prop}$) | 0 | **0** | Mathematical invariant $P_{final} \le P_{prop}$ holds with 0 violations across all 84,000 runs. |

---

## 3. Generated Evaluation Tables (Verbatim)

### Comprehensive Multi-Seed Evaluation Table (`docs/HARDENING_REPORT.md`)
*Generated by `scripts/render_tables.py` from `docs/eval_summary_multiseed.json` (3 seeds: [42, 101, 2024], 1,000 scenarios/setting):*

| Method | Drift Level | Class A Catch (Registry) | Class B Catch (Content) | Drift Catch Rate | False Exclusion Rate | Mean Abs Price Error (₹) | Invariant Violations ($P_{fin} > P_{prop}$) | Assumed Compute Cost* | Live Queries Issued / Req |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B1 (None)** | 0.00 | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹27.50 [27.48, 27.55] | 0.0 [0, 0] | 0.000 [0.0, 0.0] | 0.00 [0.0, 0.0] |
| **B1 (None)** | 0.10 | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹29.34 [29.05, 29.53] | 0.0 [0, 0] | 0.000 [0.0, 0.0] | 0.00 [0.0, 0.0] |
| **B1 (None)** | 0.20 | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹32.25 [32.08, 32.54] | 0.0 [0, 0] | 0.000 [0.0, 0.0] | 0.00 [0.0, 0.0] |
| **B1 (None)** | 0.30 | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹35.91 [35.55, 36.16] | 0.0 [0, 0] | 0.000 [0.0, 0.0] | 0.00 [0.0, 0.0] |
| **B2 (Light)** | 0.00 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹0.00 [0.0, 0.0] | 0.0 [0, 0] | 0.173 [0.173, 0.173] | 0.00 [0.0, 0.0] |
| **B2 (Light)** | 0.10 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹1.75 [1.45, 1.97] | 0.0 [0, 0] | 0.173 [0.173, 0.173] | 0.00 [0.0, 0.0] |
| **B2 (Light)** | 0.20 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹4.67 [4.48, 4.99] | 0.0 [0, 0] | 0.173 [0.173, 0.173] | 0.00 [0.0, 0.0] |
| **B2 (Light)** | 0.30 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹8.28 [8.06, 8.48] | 0.0 [0, 0] | 0.173 [0.173, 0.173] | 0.00 [0.0, 0.0] |
| **B3 (Deep)** | 0.00 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹0.00 [0.0, 0.0] | 0.0 [0, 0] | 3.457 [3.457, 3.457] | 2.17 [2.17, 2.17] |
| **B3 (Deep)** | 0.10 | 1.000 [1.0, 1.0] | 0.999 [0.997, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹0.01 [0.0, 0.02] | 0.0 [0, 0] | 3.457 [3.457, 3.457] | 2.17 [2.17, 2.17] |
| **B3 (Deep)** | 0.20 | 1.000 [1.0, 1.0] | 0.999 [0.997, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹0.01 [0.0, 0.02] | 0.0 [0, 0] | 3.457 [3.457, 3.457] | 2.17 [2.17, 2.17] |
| **B3 (Deep)** | 0.30 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | ₹0.00 [0.0, 0.0] | 0.0 [0, 0] | 3.457 [3.457, 3.457] | 2.17 [2.17, 2.17] |
| **VeriCore** | 0.00 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹0.00 [0.0, 0.0] | 0.0 [0, 0] | 1.570 [1.567, 1.571] | 0.52 [0.52, 0.52] |
| **VeriCore** | 0.10 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.183 [0.161, 0.207] | 0.000 [0.0, 0.0] | ₹1.34 [1.16, 1.52] | 0.0 [0, 0] | 1.564 [1.563, 1.565] | 0.52 [0.52, 0.52] |
| **VeriCore** | 0.20 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.229 [0.214, 0.254] | 0.000 [0.0, 0.0] | ₹3.31 [3.04, 3.63] | 0.0 [0, 0] | 1.566 [1.563, 1.568] | 0.53 [0.52, 0.53] |
| **VeriCore** | 0.30 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.255 [0.234, 0.278] | 0.000 [0.0, 0.0] | ₹5.64 [5.54, 5.72] | 0.0 [0, 0] | 1.560 [1.559, 1.561] | 0.52 [0.51, 0.53] |
| **VeriCore (No Live)** | 0.00 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹0.00 [0.0, 0.0] | 0.0 [0, 0] | 1.570 [1.567, 1.571] | 0.00 [0.0, 0.0] |
| **VeriCore (No Live)** | 0.10 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹1.75 [1.45, 1.97] | 0.0 [0, 0] | 1.564 [1.563, 1.565] | 0.00 [0.0, 0.0] |
| **VeriCore (No Live)** | 0.20 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹4.67 [4.48, 4.99] | 0.0 [0, 0] | 1.566 [1.563, 1.568] | 0.00 [0.0, 0.0] |
| **VeriCore (No Live)** | 0.30 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹8.28 [8.06, 8.48] | 0.0 [0, 0] | 1.560 [1.559, 1.561] | 0.00 [0.0, 0.0] |
| **Ablation (0.05/0.30)** | 0.00 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹0.00 [0.0, 0.0] | 0.0 [0, 0] | 2.074 [2.067, 2.082] | 1.06 [1.05, 1.06] |
| **Ablation (0.05/0.30)** | 0.10 | 1.000 [1.0, 1.0] | 0.999 [0.997, 1.0] | 0.491 [0.468, 0.524] | 0.000 [0.0, 0.0] | ₹0.77 [0.69, 0.89] | 0.0 [0, 0] | 2.074 [2.067, 2.084] | 1.05 [1.05, 1.05] |
| **Ablation (0.05/0.30)** | 0.20 | 1.000 [1.0, 1.0] | 0.999 [0.997, 1.0] | 0.496 [0.462, 0.53] | 0.000 [0.0, 0.0] | ₹2.01 [1.81, 2.12] | 0.0 [0, 0] | 2.057 [2.045, 2.066] | 1.05 [1.05, 1.05] |
| **Ablation (0.05/0.30)** | 0.30 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.529 [0.487, 0.566] | 0.000 [0.0, 0.0] | ₹3.22 [2.98, 3.42] | 0.0 [0, 0] | 2.067 [2.062, 2.072] | 1.05 [1.04, 1.06] |
| **Ablation (0.20/0.50)** | 0.00 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.000 [0.0, 0.0] | 0.000 [0.0, 0.0] | ₹0.00 [0.0, 0.0] | 0.0 [0, 0] | 1.165 [1.163, 1.166] | 0.25 [0.25, 0.25] |
| **Ablation (0.20/0.50)** | 0.10 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.022 [0.012, 0.037] | 0.000 [0.0, 0.0] | ₹1.70 [1.41, 1.94] | 0.0 [0, 0] | 1.167 [1.166, 1.168] | 0.25 [0.25, 0.25] |
| **Ablation (0.20/0.50)** | 0.20 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.044 [0.039, 0.05] | 0.000 [0.0, 0.0] | ₹4.38 [4.24, 4.63] | 0.0 [0, 0] | 1.167 [1.166, 1.167] | 0.25 [0.25, 0.25] |
| **Ablation (0.20/0.50)** | 0.30 | 1.000 [1.0, 1.0] | 1.000 [1.0, 1.0] | 0.055 [0.043, 0.07] | 0.000 [0.0, 0.0] | ₹7.65 [7.47, 7.82] | 0.0 [0, 0] | 1.167 [1.165, 1.168] | 0.25 [0.25, 0.25] |

*\*Assumed relative units, not measured time.*

### Summary Table for README.md (0% Drift Baseline)
*Generated by `scripts/render_tables.py`:*

| Metric | Baseline B1 (None) | Baseline B2 (Light) | Baseline B3 (Deep) | VeriCore (Adaptive) |
| :--- | :--- | :--- | :--- | :--- |
| **Class A Catch (Registry-Rejected)** | 0.0% | 100.0% | 100.0% | **100.0%** |
| **Class B Catch (Content-False)** | 0.0% | 100.0% | 100.0% | **100.0%** |
| **Monotonic Invariant Violations** | 0 | 0 | 0 | **0 ($P_{final} \le P_{prop}$ holds in all runs)** |
| **Assumed Compute Cost (relative units)** | 0.000 units | 0.173 units | 3.457 units | **1.570 units** |
| **Live Origin Queries Issued / Req** | 0.00 | 0.00 | 2.17 / req | **0.52 / req** |
| **Mean Absolute Price Error (0% drift)** | ₹27.50 | ₹0.00 | ₹0.00 | **₹0.00** |
| **False Exclusion Rate (Valid Factors)** | 0.0% | 0.0% | 0.0% | **0.0%** |

*\*Cost is reported in assumed relative units, not measured time.*

---

## 4. Test Results

The repository features 39 automated tests covering end-to-end functionality, patent claims C1–C4, API contracts, domain ground truth, and failure recovery. All 39 tests pass cleanly:

```powershell
$env:PYTHONPATH="backend/src"; backend\.venv\Scripts\python.exe -m pytest -q
# Result: 39 passed, 4 warnings in 4.88s
```

### Breakdown of Test Suites
1. **`tests/backend/test_eval_ground_truth.py` (7 tests, Step 6 Sanity Suite):**
   - `test_eval_ground_truth_zero_drift_agreement`: Verifies that at 0% drift in control group, false-exclusion rate is 0.0 and mean price error is 0.0 for B2, B3, and VeriCore.
   - `test_eval_class_b_caught_by_content`: Proves that Class (b) fabricated phantoms are caught by B2 via cached content entailment checks.
   - `test_eval_class_a_caught_by_registry`: Confirms Class (a) unregistered factors are caught fail-closed by the verifier registry with 0 live queries.
   - `test_eval_b1_zero_cost_and_checks`: Validates that B1 (mode `none`) runs 0 checks, consumes 0.0 cost, and accepts all proposed factors.
   - `test_live_regrounding_timeout_handling`: Simulates slow fetches exceeding `timeout_seconds` and verifies graceful return of `"unsupported"` (`"live source unavailable/timeout"`) without raising, recording 1 query attempt.
   - `test_live_regrounding_sensor_discrepancy_rule`: Verifies sensor discrepancy live branch returns `supported` when camera $\le$ sensor and `unsupported` when camera > sensor beyond tolerance.
   - `test_live_regrounding_occupancy_rule`: Confirms occupancy rule: inside tolerance and $\ge 0.70$ supported; outside tolerance unsupported; below $0.70$ unsupported.
2. **`tests/backend/test_hardening_patent_claims.py` (12 tests):**
   - Validates Component 1 (materiality routing tiers), Component 2 (live drift detection), Component 3 (resummation mathematical invariants $P_{final} \le P_{prop}$ and binary inclusion), Component 4 (hash chaining, tampering detection, head sidecar truncation detection, last-wins deduplication), and fail-closed security.
3. **`tests/backend/test_api_contract.py` (7 tests):**
   - Verifies FastAPI endpoints (`/api/lots/search`, `/api/lots/{id}/decision`, `/api/lots/{id}/verify`, `/api/admin/ledger/audit`, `/api/admin/stats`) uphold additive response schemas, backwards compatibility, and ledger immutability.
4. **`tests/backend/test_decision_resummation.py` (5 tests):**
   - Verifies invariant enforcement, clamp boundaries, and partial credit prohibition in resummation arithmetic.
5. **`tests/backend/test_ledger.py` (4 tests):**
   - Verifies cryptographic hash chain integrity, genesis block validation, and tampering sensitivity.
6. **`tests/backend/test_materiality_scoring.py` (2 tests):**
   - Tests materiality sensitivity formulas and edge-case epsilon division protection.
7. **`tests/backend/test_synthetic_dataset.py` (2 tests):**
   - Validates schema consistency and geo-spatial coordinates across the 8 synthetic parking lots.

---

## 5. Remaining Limitations Stated Plainly

1. **Deterministic Rule-Based Verifiers:** Entailment verification uses deterministic rule assessment over structured signals rather than deep cross-encoder neural language models (e.g. RoBERTa or DeBERTa). While formal `Protocol` interfaces (`EntailmentVerifier`, `ClaimJudge`) and an optional `requirements-ml.txt` exist for drop-in ML integration, the core runtime remains deterministic.
2. **Simulated Origin Data Sources:** In accordance with patent filing constraints prohibiting external network calls and telemetry, live sensor checks, camera feeds, and municipal schedule APIs are simulated via an in-memory `LiveStateStore` with configurable `DriftInjector`.
3. **Synthetic Dataset Calibration:** The 8 parking facilities represent a calibrated synthetic model of Bengaluru municipal transit hubs, commercial decks, and hospitals rather than production telemetry feeds.
4. **Low Drift Catch at Default Thresholds:** By architectural design, standard-tier claims (materiality between 0.10 and 0.40) are verified against cached context; only high-materiality claims ($\ge 0.40$) trigger out-of-band live sensor queries. Under default thresholds, most drifted claims fall into standard or light tiers, resulting in low drift catch rate (~18-25%). The 0.05/0.30 ablation demonstrates the coverage/cost trade-off, catching ~49-53% of drift at higher compute and query cost.
5. **Ledger Tamper Threat Model:** The ledger cryptographic chain detects payload modifications, genesis alterations, and tail truncation (via the `.head` sidecar file). It does not prevent an offline adversary with filesystem write access from re-computing and replacing both `ledger.jsonl` and `ledger.head` simultaneously.

---

## 6. Exact Commands to Reproduce Every Number

All reported numbers are produced directly by scripts without hand editing. To reproduce from workspace root:

```powershell
# 1. Run the entire test suite (39 tests):
$env:PYTHONPATH="backend/src"; backend\.venv\Scripts\python.exe -m pytest -q

# 2. Run the full Monte Carlo evaluation across 1,000 scenarios and 3 seeds:
$env:PYTHONPATH="backend/src"; backend\.venv\Scripts\python.exe scripts/run_evaluation.py --scenarios 1000 --seeds 42 101 2024

# 3. Inject generated tables into documentation and README:
backend\.venv\Scripts\python.exe scripts/render_tables.py

# 4. Verify cryptographic chain and sidecar head of the ledger:
backend\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend/src'); from veripark.vericore.ledger import DecisionLedger; valid, msg = DecisionLedger('data/ledger/ledger.jsonl').verify_chain(); print('Ledger status:', valid, msg)"
```
