# Frontend Wiring Fixes — VeriPark

## Issues Found & Fixes

### 1. Routing Inconsistency (CRITICAL)
- `results/page.tsx` links to `/decision/${lot.id}` (e.g. `lot-metro-hub`)
- Backend returns `decision_id: "dec-lot-metro-hub"` from search API  
- `decision/[id]/page.tsx` sub-nav uses `lot.id` for verify/audit/confirm links
  but the URL param `id` is whatever came from the results page
- **Fix**: Make results link to `/decision/${lot.id}` (using lot ID consistently), and in decision detail page use the URL `id` param for all sub-navigation links.

### 2. CSS Variable Missing
- `--color-slate-100` used in StatusChip but not defined
- `--radius-2xl` used in page.tsx hero but not defined
- `--font-sans` not set; layout uses `font-sans` but fonts are Manrope/Source Serif
- **Fix**: Add missing CSS variables to globals.css

### 3. Dead Imports
- `results/page.tsx` imports `getLots` from mock-data but never uses it
- `confirmed/page.tsx` imports `getDecisionByLotId` from mock-data redundantly
- **Fix**: Clean up unused imports

### 4. Booking Confirmation — No Access Code Display
- `confirmed/page.tsx` re-fetches the decision but doesn't show booking ref/access code from the booking API
- **Fix**: Use URL search params to pass booking_id and access_code to the confirmed page

### 5. Font Variable Mismatch
- `layout.tsx` adds body class `font-sans` but fonts are `--font-manrope` and `--font-source-serif`
- Need to configure Tailwind to map `font-sans` → Manrope
- **Fix**: Add `@theme` font-family mapping

### 6. Operator Dashboard — API data vs mock data mismatch  
- `fetchAdminStats()` returns `trend` as `{date, count, adjustment_rate}` but operator page uses `OPERATOR_TREND` (mock) which has `{label, decisions, adjustedPct}` shape
- **Fix**: operator page already uses OPERATOR_TREND from mock for the chart (correct), stats from API for KPIs (correct)

### 7. Missing `formatShortTime` graceful handling
- If `decision.timestamp` is "now" (current), it renders fine; but ISO date from API is UTC

### 8. Next.js server component image tag uses `onError` (client-only)
- `decision/[id]/page.tsx` uses `onError` on `<img>` in a server component — this is invalid
- **Fix**: Either make it client component or use a client-side image wrapper
