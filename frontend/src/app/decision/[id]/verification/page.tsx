import { notFound } from "next/navigation";
import { CheckCircle2, MinusCircle, Radar, ScanSearch, ShieldCheck, Zap } from "lucide-react";
import { fetchDecision } from "@/lib/api";
import { formatRupees } from "@/lib/utils";
import { BackHeader, Card, Screen } from "@/components/ui/Screen";
import { StatusChip } from "@/components/ui/StatusChip";
import { InfoTag } from "@/components/ui/InfoTag";
import type { VerificationTier } from "@/lib/types";

const TIER_META: Record<VerificationTier, { label: string; icon: typeof Zap; meaning: string }> = {
  quick: {
    label: "Quick check",
    icon: Zap,
    meaning: "A fast, single-source check — used when this factor barely moves your price.",
  },
  careful: {
    label: "Careful check",
    icon: ScanSearch,
    meaning: "Cross-checked against more than one source — used when this factor has a moderate effect on price.",
  },
  live: {
    label: "Rechecked live just now",
    icon: Radar,
    meaning: "Re-confirmed against the original, real-time data source at the moment of checking — reserved for factors with the biggest effect on your price.",
  },
};

export default async function VerificationDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const decision = await fetchDecision(id);
  if (!decision) notFound();

  return (
    <Screen>
      <BackHeader backHref={`/decision/${id}`} title="How we verified this" />

      <div className="flex-1 space-y-4 px-5 py-5">
        <div className="flex items-start gap-3 rounded-2xl border border-[--color-accent-100] bg-[--color-brand-50] p-4 shadow-soft">
          <ShieldCheck size={20} className="mt-0.5 shrink-0 text-[--color-accent]" />
          <p className="text-[13px] leading-relaxed font-medium text-[--color-brand-dark]">
            We don&apos;t just trust our own explanation — we check it, and the more it affects your price, the more
            carefully we check it.
          </p>
        </div>

        <div className="space-y-3">
          {decision.factors.map((factor) => {
            const tier = TIER_META[factor.tier] || TIER_META.quick;
            const TierIcon = tier.icon;
            const excluded = factor.status === "excluded";

            return (
              <Card key={factor.id} className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-[14px] font-bold text-[--color-charcoal]">{factor.label}</p>
                    <p className="mt-0.5 text-xs leading-relaxed text-[--color-slate]">{factor.description}</p>
                  </div>
                  <span
                    className={`shrink-0 text-[15px] font-bold ${
                      excluded ? "text-[--color-slate-light] line-through" : "text-[--color-charcoal]"
                    }`}
                  >
                    {formatRupees(factor.amount)}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2 border-t border-[--color-border-soft] pt-3">
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-[--color-border-soft] bg-[--color-bg-off] px-2.5 py-1 text-[11px] font-semibold text-[--color-charcoal]">
                    <TierIcon size={12} className="text-[--color-accent]" />
                    {tier.label}
                  </span>
                  <InfoTag meaning={tier.meaning} />
                  <StatusChip
                    size="sm"
                    tone={excluded ? "excluded" : factor.tier === "live" ? "live" : "verified"}
                    label={excluded ? "Removed" : factor.tier === "live" ? "Confirmed live" : "Confirmed"}
                    meaning={
                      excluded
                        ? "This factor did not hold up, so its amount was removed from your price."
                        : "This factor was checked and confirmed."
                    }
                  />
                </div>

                <p className="flex items-start gap-2 text-xs leading-relaxed text-[--color-slate]">
                  {excluded ? (
                    <MinusCircle size={14} className="mt-0.5 shrink-0 text-[--color-danger]" />
                  ) : (
                    <CheckCircle2 size={14} className="mt-0.5 shrink-0 text-[--color-verified]" />
                  )}
                  <span className={excluded ? "text-[--color-danger]" : "text-[--color-slate]"}>
                    {factor.checkDetail}
                  </span>
                </p>
              </Card>
            );
          })}
        </div>

        <Card className="flex items-center justify-between text-xs font-semibold text-[--color-slate]">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 size={13} className="text-[--color-verified]" />
            {decision.verificationSummary.verifiedClaims} of {decision.verificationSummary.totalClaims} reasons confirmed
          </span>
          <span className="text-[--color-live]">
            {decision.verificationSummary.liveRecheckedClaims} rechecked live
          </span>
        </Card>
      </div>
    </Screen>
  );
}
