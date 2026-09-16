# Architectural & Implementation Decisions Log (VeriPark)

## 1. Stitch Export Assessment (Phase A0)
- **Inventory Check against 9-screen flow:**
  1. Onboarding: Present at `frontend/src/app/page.tsx`
  2. Search: Present at `frontend/src/app/search/page.tsx`
  3. Results: Present at `frontend/src/app/results/page.tsx`
  4. Decision Detail: Present at `frontend/src/app/decision/[id]/page.tsx`
  5. Verification Detail: Present at `frontend/src/app/decision/[id]/verification/page.tsx`
  6. Audit Trail: Present at `frontend/src/app/decision/[id]/audit/page.tsx`
  7. Confirm & Book: Present at `frontend/src/app/decision/[id]/confirm/page.tsx`
  8. Booking Confirmed: Present at `frontend/src/app/decision/[id]/confirmed/page.tsx`
  9. Operator Dashboard: Present at `frontend/src/app/operator/page.tsx`
- **Stack Decision:** The Stitch export is a Next.js (16.2.6) + React 19 + Tailwind CSS 4 application with TypeScript. We retain this exact stack in `frontend/`, keeping `frontend/stitch-source/` as the pristine reference.
- **Data-Binding Approach:** Frontend originally imported mock data directly from `src/lib/mock-data.ts`. We wire all pages to fetch from the FastAPI backend at `http://127.0.0.1:8000` (configurable via `NEXT_PUBLIC_API_BASE_URL`), with seamless fallback or server-side fetching matching the Section 5 API contract.

## 2. Backend & VeriCore Specifications (Phase B & C)
- **Virtual Environment:** Set up in `backend/.venv` (Python 3.14).
- **Patent-Critical Mechanism Invariants:**
  - `materiality(claim) = abs(factor.contribution) / max(abs(proposed_price - base_price), epsilon)`
  - Adaptive routing thresholds: `< 0.10` -> light, `< 0.40` -> standard, `>= 0.40` -> deep (with live re-grounding).
  - Decision Resummation: Strict mathematical resummation, no generalized confidence or grade weighting. Only supported factors are summed with base price. `final_price = min(resummed_price, proposed_price)`.
  - Ledger: Append-only JSONL with SHA-256 block hashing referencing `previous_hash`.
- **Friendly Labels:** Strict boundary in `friendly_labels.py` so internal tier and verdict names (`deep`, `unsupported`, etc.) are never leaked to client JSON responses.
