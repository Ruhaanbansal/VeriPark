import Link from "next/link";
import { notFound } from "next/navigation";
import { CheckCircle2, ChevronRight, FileLock2, MinusCircle, Radar, ShieldCheck } from "lucide-react";
import { getDecisionByLotId } from "@/lib/mock-data";
import { formatRupees } from "@/lib/utils";
import { BackHeader, BottomActionBar, Card, Screen } from "@/components/ui/Screen";
import { StatusChip } from "@/components/ui/StatusChip";
import { Button } from "@/components/ui/Button";
import type { ClaimStatus } from "@/lib/types";

const SENTENCE_ICON: Record<ClaimStatus, React.ComponentType<{ size?: number; strokeWidth?: number; className?: string }>> = {
  verified: CheckCircle2,
  checked_live: Radar,
  excluded: MinusCircle,
};

const SENTENCE_MEANING: Record<ClaimStatus, string> = {
  verified: "Confirmed against reliable evidence.",
  checked_live: "Rechecked against a live data source just now, because it affects your price the most.",
  excluded: "Could not be confirmed, so it was removed from your price.",
};

export default async function DecisionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const decision = getDecisionByLotId(id);
  if (!decision) notFound();

  const { lot } = decision;

  return (
    <Screen>
      <BackHeader backHref="/results" title={lot.name} />

      <div className="flex-1 space-y-5 px-5 py-5">
        {/* Price block */}
        <Card className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-[--color-slate]">
              Price for {decision.durationHours} hours
            </p>
            <StatusChip
              tone={decision.wasAdjusted ? "adjusted" : "verified"}
              label={decision.wasAdjusted ? "Adjusted" : "Verified"}
              meaning={
                decision.wasAdjusted
                  ? "Part of this price couldn't be verified, so it was automatically lowered before you saw it."
                  : "Every part of this price was checked and confirmed against real evidence."
              }
            />
          </div>

          <div className="flex flex-wrap items-end gap-3">
            <span className="text-[42px] font-bold leading-none text-[--color-navy]">
              {formatRupees(decision.finalPrice)}
            </span>
            {decision.wasAdjusted && (
              <span className="pb-1.5 text-lg font-medium text-[--color-slate-light] line-through decoration-2">
                {formatRupees(decision.originalPrice)}
              </span>
            )}
          </div>

          {decision.wasAdjusted && (
            <div className="flex items-start gap-2 rounded-xl bg-[--color-amber-50] p-3 text-[13px] leading-relaxed text-[--color-amber-dark]">
              <ShieldCheck size={16} className="mt-0.5 shrink-0" />
              <p>{decision.adjustmentReason}</p>
            </div>
          )}
        </Card>

        {/* Explanation */}
        <div>
          <p className="mb-2.5 text-xs font-semibold uppercase tracking-wide text-[--color-slate]">
            Why this price
          </p>
          <Card className="space-y-3.5">
            {decision.explanation.map((sentence) => {
              const Icon = SENTENCE_ICON[sentence.status];
              const isExcluded = sentence.status === "excluded";
              return (
                <div key={sentence.id} className="flex items-start gap-2.5">
                  <Icon
                    size={17}
                    strokeWidth={2.2}
                    className={`mt-0.5 shrink-0 ${
                      sentence.status === "verified"
                        ? "text-[--color-teal]"
                        : sentence.status === "checked_live"
                          ? "text-[--color-navy]"
                          : "text-[--color-slate-light]"
                    }`}
                  />
                  <p
                    title={SENTENCE_MEANING[sentence.status]}
                    className={`text-[14px] leading-relaxed ${
                      isExcluded ? "text-[--color-slate-light] line-through decoration-1" : "text-[--color-charcoal]"
                    }`}
                  >
                    {sentence.text}
                  </p>
                </div>
              );
            })}
          </Card>
        </div>

        {/* Progressive disclosure links */}
        <div className="space-y-2 pt-1">
          <Link
            href={`/decision/${lot.id}/verification`}
            className="flex items-center justify-between rounded-xl border border-[--color-border-soft] bg-white px-4 py-3.5 shadow-soft transition-colors hover:border-[--color-teal-100]"
          >
            <span className="flex items-center gap-2.5 text-[14px] font-semibold text-[--color-teal-dark]">
              <ShieldCheck size={17} /> See how we verified this
            </span>
            <ChevronRight size={16} className="text-[--color-slate-light]" />
          </Link>

          <Link
            href={`/decision/${lot.id}/audit`}
            className="flex items-center justify-between px-4 py-2 text-xs font-medium text-[--color-slate] transition-colors hover:text-[--color-charcoal]"
          >
            <span className="flex items-center gap-2">
              <FileLock2 size={13} /> View audit record
            </span>
            <ChevronRight size={13} />
          </Link>
        </div>
      </div>

      <BottomActionBar>
        <Button href={`/decision/${lot.id}/confirm`} size="lg" fullWidth>
          Book this spot — {formatRupees(decision.finalPrice)}
        </Button>
      </BottomActionBar>
    </Screen>
  );
}
