import Link from "next/link";
import { AlertTriangle, ArrowLeft, Gauge, ShieldCheck, TrendingUp, Zap } from "lucide-react";
import { getDecisionByLotId, getLots, OPERATOR_SUMMARY, OPERATOR_TREND } from "@/lib/mock-data";
import { formatRupees } from "@/lib/utils";
import { Logo } from "@/components/ui/Logo";
import { StatusChip } from "@/components/ui/StatusChip";
import { InfoTag } from "@/components/ui/InfoTag";

const KPIS = [
  {
    label: "Decisions processed",
    value: OPERATOR_SUMMARY.totalDecisions.toLocaleString("en-IN"),
    icon: Gauge,
    meaning: "Total pricing and allocation decisions made in the last 7 days.",
    tone: "navy" as const,
  },
  {
    label: "Required a price adjustment",
    value: `${OPERATOR_SUMMARY.adjustedPct}%`,
    sub: `avg ${formatRupees(OPERATOR_SUMMARY.avgAdjustmentAmount)} per adjustment`,
    icon: AlertTriangle,
    meaning: "Share of decisions where at least one claim failed verification and the price was automatically corrected.",
    tone: "amber" as const,
  },
  {
    label: "Verification cost saved",
    value: `${OPERATOR_SUMMARY.verificationCostSavingsPct}%`,
    sub: "vs. checking every claim at the deepest tier",
    icon: Zap,
    meaning: "We only run the expensive check when it matters — saving compute versus checking everything the same way.",
    tone: "teal" as const,
  },
  {
    label: "Unsupported claims caught",
    value: OPERATOR_SUMMARY.hallucinationCatchCount.toLocaleString("en-IN"),
    sub: "this week, before reaching a driver",
    icon: ShieldCheck,
    meaning: "Explanation claims that failed verification and were corrected before being shown to a driver.",
    tone: "navy" as const,
  },
];

const TONE_BG: Record<string, string> = {
  navy: "bg-[--color-navy-50] text-[--color-navy]",
  amber: "bg-[--color-amber-50] text-[--color-amber-dark]",
  teal: "bg-[--color-teal-50] text-[--color-teal-dark]",
};

export default function OperatorDashboardPage() {
  const maxDecisions = Math.max(...OPERATOR_TREND.map((d) => d.decisions));
  const adjustedLots = getLots()
    .map((l) => getDecisionByLotId(l.id))
    .filter((d) => d && d.wasAdjusted);

  return (
    <div className="min-h-screen bg-[--color-bg-off]">
      <header className="border-b border-[--color-border-soft] bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <Logo />
            <span className="hidden rounded-full bg-[--color-navy-50] px-3 py-1 text-xs font-semibold text-[--color-navy] sm:inline-block">
              Operator Dashboard
            </span>
          </div>
          <Link
            href="/"
            className="flex items-center gap-1.5 text-sm font-semibold text-[--color-slate] hover:text-[--color-navy]"
          >
            <ArrowLeft size={15} /> Back to driver app
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="font-serif-display text-[26px] font-semibold text-[--color-navy]">
              Trust &amp; verification overview
            </h1>
            <p className="mt-1 text-sm text-[--color-slate]">Last 7 days · MG Road &amp; Indiranagar zones</p>
          </div>
          <StatusChip
            tone="verified"
            label="VeriCore active"
            meaning="The verification and decision-clamping engine is running on all live decisions."
          />
        </div>

        {/* KPI cards */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {KPIS.map((kpi) => (
            <div key={kpi.label} className="rounded-2xl border border-[--color-border-soft] bg-white p-5 shadow-soft">
              <div className="flex items-center justify-between">
                <span className={`grid h-9 w-9 place-items-center rounded-xl ${TONE_BG[kpi.tone]}`}>
                  <kpi.icon size={17} strokeWidth={2} />
                </span>
                <InfoTag meaning={kpi.meaning} />
              </div>
              <p className="mt-3 text-2xl font-bold text-[--color-charcoal]">{kpi.value}</p>
              <p className="text-xs font-medium text-[--color-slate]">{kpi.label}</p>
              {kpi.sub && <p className="mt-1 text-[11px] text-[--color-slate-light]">{kpi.sub}</p>}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
          {/* Trend chart */}
          <div className="rounded-2xl border border-[--color-border-soft] bg-white p-6 shadow-soft lg:col-span-3">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-[--color-charcoal]">Decision volume &amp; adjustment rate</p>
                <p className="text-xs text-[--color-slate]">Daily, last 7 days</p>
              </div>
              <span className="flex items-center gap-1.5 text-xs font-semibold text-[--color-teal-dark]">
                <TrendingUp size={14} /> Trending up
              </span>
            </div>

            <div className="flex items-end gap-4">
              {OPERATOR_TREND.map((point) => (
                <div key={point.label} className="flex flex-1 flex-col items-center gap-2">
                  <span className="text-[10px] font-semibold text-[--color-amber-dark]">{point.adjustedPct}%</span>
                  <div className="flex h-40 w-full items-end overflow-hidden rounded-lg bg-[--color-bg-off]">
                    <div
                      className="w-full rounded-t-lg bg-[--color-navy]"
                      style={{ height: `${(point.decisions / maxDecisions) * 100}%` }}
                    />
                  </div>
                  <span className="text-[11px] font-medium text-[--color-slate]">{point.label}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 flex items-center gap-4 border-t border-[--color-border-soft] pt-4 text-[11px] text-[--color-slate]">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm bg-[--color-navy]" /> Decisions processed
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm bg-[--color-amber]" /> % adjusted
              </span>
            </div>
          </div>

          {/* Routing savings explainer */}
          <div className="rounded-2xl border border-[--color-border-soft] bg-white p-6 shadow-soft lg:col-span-2">
            <p className="text-sm font-semibold text-[--color-charcoal]">Where verification effort goes</p>
            <p className="mt-1 text-xs text-[--color-slate]">
              We only run the expensive check when it matters — saving {OPERATOR_SUMMARY.verificationCostSavingsPct}%
              compute versus checking everything the same way.
            </p>
            <div className="mt-5 space-y-3">
              <RoutingBar label="Quick check" pct={58} tone="teal" detail="Low-stakes claims, single-source match" />
              <RoutingBar label="Careful check" pct={29} tone="navy" detail="Moderate-stakes, cross-source match" />
              <RoutingBar label="Rechecked live" pct={13} tone="amber" detail="Highest-stakes, fresh source query" />
            </div>
            <div className="mt-5 flex items-center justify-between rounded-xl bg-[--color-bg-off] px-4 py-3 text-xs text-[--color-slate]">
              <span>Avg. verification latency</span>
              <span className="font-semibold text-[--color-charcoal]">{OPERATOR_SUMMARY.avgLatencyMs} ms</span>
            </div>
          </div>
        </div>

        {/* Recent adjustments table */}
        <div className="rounded-2xl border border-[--color-border-soft] bg-white shadow-soft">
          <div className="flex items-center justify-between border-b border-[--color-border-soft] px-6 py-4">
            <p className="text-sm font-semibold text-[--color-charcoal]">Recent price adjustments</p>
            <span className="text-xs text-[--color-slate]">Component 3 — self-correcting decision clamping</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-[--color-border-soft] text-xs uppercase tracking-wide text-[--color-slate]">
                  <th className="px-6 py-3 font-semibold">Decision ID</th>
                  <th className="px-6 py-3 font-semibold">Lot</th>
                  <th className="px-6 py-3 font-semibold">Original</th>
                  <th className="px-6 py-3 font-semibold">Final</th>
                  <th className="px-6 py-3 font-semibold">Reason</th>
                </tr>
              </thead>
              <tbody>
                {adjustedLots.map((d) =>
                  d ? (
                    <tr key={d.id} className="border-b border-[--color-border-soft] last:border-0">
                      <td className="px-6 py-3.5 font-mono text-xs text-[--color-charcoal]">{d.id}</td>
                      <td className="px-6 py-3.5 text-[--color-charcoal]">{d.lot.name}</td>
                      <td className="px-6 py-3.5 text-[--color-slate-light] line-through">
                        {formatRupees(d.originalPrice)}
                      </td>
                      <td className="px-6 py-3.5 font-semibold text-[--color-navy]">{formatRupees(d.finalPrice)}</td>
                      <td className="max-w-xs truncate px-6 py-3.5 text-xs text-[--color-slate]">
                        {d.adjustmentReason}
                      </td>
                    </tr>
                  ) : null,
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

function RoutingBar({
  label,
  pct,
  tone,
  detail,
}: {
  label: string;
  pct: number;
  tone: "teal" | "navy" | "amber";
  detail: string;
}) {
  const barColor =
    tone === "teal" ? "bg-[--color-teal]" : tone === "navy" ? "bg-[--color-navy]" : "bg-[--color-amber]";
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between text-xs">
        <span className="font-semibold text-[--color-charcoal]">{label}</span>
        <span className="text-[--color-slate]">{pct}% of claims</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-[--color-bg-off]">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <p className="mt-1 text-[11px] text-[--color-slate-light]">{detail}</p>
    </div>
  );
}
