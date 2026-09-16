import Link from "next/link";
import { notFound } from "next/navigation";
import { CheckCircle2, ChevronRight, FileLock2, MinusCircle, Radar, ShieldCheck, Star } from "lucide-react";
import { fetchDecision } from "@/lib/api";
import { formatRupees } from "@/lib/utils";
import { BackHeader, BottomActionBar, Card, Screen } from "@/components/ui/Screen";
import { StatusChip } from "@/components/ui/StatusChip";
import { Button } from "@/components/ui/Button";
import type { ClaimStatus } from "@/lib/types";
import { VenueImageServer } from "@/components/ui/VenueImageServer";

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
  const decision = await fetchDecision(id);
  if (!decision) notFound();

  const { lot } = decision;
  // Always use the URL 'id' param for sub-routes — it's whatever the browser navigated to
  // (could be dec-lot-metro-hub or lot-metro-hub; backend handles both via cache)
  const routeId = id;

  return (
    <Screen>
      <BackHeader backHref="/results" title={lot.name} />

      <div className="flex-1 space-y-4 px-5 py-4">
        {/* Venue Visual Image Banner — server-side, no onError needed */}
        <div className="overflow-hidden rounded-2xl border border-[--color-border-soft] bg-[--color-bg-off] shadow-soft">
          <VenueImageServer lotId={lot.id} name={lot.name} />
        </div>

        {/* Lot meta row */}
        <div className="flex items-center justify-between px-1">
          <p className="text-xs text-[--color-slate]">{lot.address}</p>
          <div className="flex items-center gap-1">
            <Star size={12} className="fill-[--color-amber] text-[--color-amber]" />
            <span className="text-xs font-bold text-[--color-charcoal]">{lot.rating?.toFixed(1) ?? "4.8"}</span>
          </div>
        </div>

        {/* Price block */}
        <Card className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold uppercase tracking-wider text-[--color-slate]">
              Price for {decision.durationHours} hour{decision.durationHours !== 1 ? "s" : ""}
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
            <span className="text-[40px] font-extrabold leading-none text-[--color-charcoal]">
              {formatRupees(decision.finalPrice)}
            </span>
            {decision.wasAdjusted && (
              <span className="pb-1 text-lg font-semibold text-[--color-slate-light] line-through decoration-2">
                {formatRupees(decision.originalPrice)}
              </span>
            )}
          </div>

          {decision.wasAdjusted && (
            <div className="flex items-start gap-2.5 rounded-xl border border-[--color-adjusted-100] bg-[--color-adjusted-50] p-3.5 text-[13px] leading-relaxed text-[--color-adjusted]">
              <ShieldCheck size={17} className="mt-0.5 shrink-0 text-[--color-accent]" />
              <p className="font-medium">{decision.adjustmentReason}</p>
            </div>
          )}
        </Card>

        {/* VeriCore™ Summary badges */}
        <div className="grid grid-cols-3 gap-2">
          <SummaryBadge
            value={decision.verificationSummary.verifiedClaims}
            label="Confirmed"
            color="text-[--color-verified]"
            bg="bg-[--color-verified-50]"
          />
          <SummaryBadge
            value={decision.verificationSummary.liveRecheckedClaims}
            label="Live-checked"
            color="text-[--color-live]"
            bg="bg-[--color-live-50]"
          />
          <SummaryBadge
            value={decision.verificationSummary.excludedClaims}
            label="Removed"
            color="text-[--color-danger]"
            bg="bg-[--color-danger-50]"
          />
        </div>

        {/* Explanation */}
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-wider text-[--color-slate]">
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
                        ? "text-[--color-verified]"
                        : sentence.status === "checked_live"
                          ? "text-[--color-live]"
                          : "text-[--color-slate]"
                    }`}
                  />
                  <p
                    title={SENTENCE_MEANING[sentence.status]}
                    className={`text-[14px] leading-relaxed ${
                      isExcluded ? "text-[--color-slate] line-through decoration-1 opacity-75 font-medium" : "text-[--color-charcoal] font-medium"
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
        <div className="space-y-2.5 pt-1">
          <Link
            href={`/decision/${routeId}/verification`}
            className="flex items-center justify-between rounded-xl border border-[--color-border] bg-white px-4 py-3.5 shadow-soft transition-all hover:border-[--color-accent] hover:shadow-soft-lg"
          >
            <span className="flex items-center gap-2.5 text-[14px] font-bold text-[--color-charcoal]">
              <ShieldCheck size={18} className="text-[--color-accent]" /> See how we verified this
            </span>
            <ChevronRight size={16} className="text-[--color-slate]" />
          </Link>

          <Link
            href={`/decision/${routeId}/audit`}
            className="flex items-center justify-between px-4 py-2 text-xs font-semibold text-[--color-slate] transition-colors hover:text-[--color-charcoal]"
          >
            <span className="flex items-center gap-2">
              <FileLock2 size={14} className="text-[--color-slate]" /> View cryptographic audit record
            </span>
            <ChevronRight size={14} />
          </Link>
        </div>
      </div>

      <BottomActionBar>
        <Button href={`/decision/${routeId}/confirm`} size="lg" fullWidth>
          Book this spot — {formatRupees(decision.finalPrice)}
        </Button>
      </BottomActionBar>
    </Screen>
  );
}

function SummaryBadge({
  value,
  label,
  color,
  bg,
}: {
  value: number;
  label: string;
  color: string;
  bg: string;
}) {
  return (
    <div className={`flex flex-col items-center rounded-xl ${bg} px-2 py-2.5`}>
      <span className={`text-xl font-extrabold ${color}`}>{value}</span>
      <span className="mt-0.5 text-center text-[10px] font-semibold text-[--color-slate]">{label}</span>
    </div>
  );
}
