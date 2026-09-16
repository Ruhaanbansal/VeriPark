import { notFound } from "next/navigation";
import { CheckCircle2, MinusCircle, Radar, ScanSearch, ShieldCheck, Zap } from "lucide-react";
import { getDecisionByLotId } from "@/lib/mock-data";
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
  const decision = getDecisionByLotId(id);
  if (!decision) notFound();

  return (
    <Screen>
      <BackHeader backHref={`/decision/${id}`} title="How we verified this" />

      <div className="flex-1 space-y-4 px-5 py-5">
        <Card className="flex items-start gap-3 bg-[--color-navy-50] border-transparent">
          <ShieldCheck size={18} className="mt-0.5 shrink-0 text-[--color-navy]" />
          <p className="text-[13px] leading-relaxed text-[--color-navy]">
            We don&apos;t just trust our own explanation — we check it, and the more it affects your price, the more
            carefully we check it.
          </p>
        </Card>

        <div className="space-y-3">
          {decision.factors.map((factor) => {
            const tier = TIER_META[factor.tier];
            const TierIcon = tier.icon;
            const excluded = factor.status === "excluded";

            return (
              <Card key={factor.id} className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-[14px] font-semibold text-[--color-charcoal]">{factor.label}</p>
                    <p className="mt-0.5 text-xs leading-relaxed text-[--color-slate]">{factor.description}</p>
                  </div>
                  <span
                    className={`shrink-0 text-[15px] font-bold ${
                      excluded ? "text-[--color-slate-light] line-through" : "text-[--color-navy]"
                    }`}
                  >
                    {formatRupees(factor.amount === 0 && excluded ? factor.amount : factor.amount)}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2 border-t border-[--color-border-soft] pt-3">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-[--color-bg-off] px-2.5 py-1 text-[11px] font-semibold text-[--color-charcoal]">
                    <TierIcon size={12} />
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
                    <MinusCircle size={13} className="mt-0.5 shrink-0 text-[--color-slate-light]" />
                  ) : (
                    <CheckCircle2 size={13} className="mt-0.5 shrink-0 text-[--color-teal]" />
                  )}
                  {factor.checkDetail}
                </p>
              </Card>
            );
          })}
        </div>

        <Card className="flex items-center justify-between text-xs text-[--color-slate]">
          <span>{decision.verificationSummary.verifiedClaims} of {decision.verificationSummary.totalClaims} reasons confirmed</span>
          <span>{decision.verificationSummary.liveRecheckedClaims} rechecked live</span>
        </Card>
      </div>
    </Screen>
  );
}
