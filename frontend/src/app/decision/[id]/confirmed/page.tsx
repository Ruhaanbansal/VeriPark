"use client";

import { Suspense, useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { CalendarClock, CheckCircle2, FileLock2, Loader2, MapPin } from "lucide-react";
import { fetchDecision } from "@/lib/api";
import { formatRupees, formatShortTime } from "@/lib/utils";
import { Card, Screen } from "@/components/ui/Screen";
import { Button } from "@/components/ui/Button";
import type { Decision } from "@/lib/types";

function ConfirmedContent() {
  const params = useParams();
  const id = params.id as string;
  const searchParams = useSearchParams();

  // Booking data passed by confirm page via URL params
  const bookingId = searchParams.get("bookingId");
  const accessCode = searchParams.get("accessCode");
  const paidPrice = searchParams.get("price");

  const [decision, setDecision] = useState<Decision | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchDecision(id).then((d) => {
      if (mounted) {
        setDecision(d);
        setLoading(false);
      }
    });
    return () => { mounted = false; };
  }, [id]);

  const bookingRef = bookingId || (decision ? `VP-${decision.id.split("-").pop()?.toUpperCase() || "7721"}` : "VP-CONFIRMED");
  const displayAccessCode = accessCode || bookingRef;
  const displayPrice = paidPrice ? Number(paidPrice) : decision?.finalPrice ?? 0;

  if (loading) {
    return (
      <Screen className="items-center justify-center">
        <div className="flex flex-col items-center gap-4 p-8 text-center">
          <Loader2 size={32} className="animate-spin text-[--color-accent]" />
          <p className="text-sm font-semibold text-[--color-slate]">Confirming your reservation…</p>
        </div>
      </Screen>
    );
  }

  return (
    <Screen className="justify-between px-6 pb-8 pt-12">
      <div className="flex flex-col items-center text-center">
        {/* Success icon with glowing ring */}
        <span className="grid h-20 w-20 place-items-center rounded-full bg-[--color-verified-50] text-[--color-verified] ring-8 ring-[--color-verified-50]/40 shadow-soft animate-fade-in">
          <CheckCircle2 size={42} strokeWidth={2.2} />
        </span>

        <h1 className="mt-5 font-serif-display text-2xl font-bold text-[--color-charcoal] animate-fade-in-up">
          Spot Confirmed
        </h1>
        <p className="mt-1.5 max-w-[280px] text-sm leading-relaxed text-[--color-slate] animate-fade-in-up delay-75">
          Your parking spot is reserved and VeriCore™ verified. Show your access code at the gate.
        </p>

        {/* Booking card */}
        <Card className="mt-6 w-full text-left animate-slide-up delay-150">
          {/* Reference row */}
          <div className="flex items-center justify-between border-b border-dashed border-[--color-border] pb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-[--color-slate]">
              Booking reference
            </span>
            <span className="font-mono text-sm font-bold text-[--color-brand-dark] bg-[--color-brand-50] px-2.5 py-0.5 rounded-lg border border-[--color-brand-100]">
              {bookingRef}
            </span>
          </div>

          {/* Access code — large & scannable */}
          <div className="py-4 text-center border-b border-dashed border-[--color-border]">
            <p className="text-[10px] font-bold uppercase tracking-widest text-[--color-slate] mb-2">Gate access code</p>
            <p className="font-mono text-2xl font-extrabold tracking-[0.3em] text-[--color-charcoal]">
              {displayAccessCode}
            </p>
          </div>

          {/* Lot details */}
          <div className="space-y-3 pt-3">
            {decision && (
              <>
                <div className="flex items-start gap-2.5">
                  <MapPin size={16} className="mt-0.5 shrink-0 text-[--color-accent]" />
                  <div>
                    <p className="text-[14px] font-bold text-[--color-charcoal]">{decision.lot.name}</p>
                    <p className="text-xs text-[--color-slate]">{decision.lot.address}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2.5">
                  <CalendarClock size={16} className="shrink-0 text-[--color-slate]" />
                  <p className="text-[13px] font-medium text-[--color-charcoal]">
                    {formatShortTime(decision.timestamp)} · {decision.durationHours} hour{decision.durationHours !== 1 ? "s" : ""}
                  </p>
                </div>
              </>
            )}
            <div className="flex items-center justify-between border-t border-[--color-border-soft] pt-3">
              <span className="text-xs font-semibold text-[--color-slate]">Amount verified &amp; paid</span>
              <span className="text-lg font-extrabold text-[--color-charcoal]">{formatRupees(displayPrice)}</span>
            </div>
          </div>
        </Card>

        {/* Audit link */}
        <Link
          href={`/decision/${id}/audit`}
          className="mt-4 flex items-center gap-2 text-[13px] font-bold text-[--color-brand-mid] hover:text-[--color-accent] transition-colors"
        >
          <FileLock2 size={15} /> View sealed audit record
        </Link>
      </div>

      <div className="space-y-3 mt-8">
        <Button href="/search" fullWidth size="lg" variant="primary">
          Find another spot
        </Button>
        <Button href="/" fullWidth variant="ghost">
          Back to home
        </Button>
      </div>
    </Screen>
  );
}

export default function BookingConfirmedPage() {
  return (
    <Suspense
      fallback={
        <Screen className="items-center justify-center">
          <Loader2 size={32} className="animate-spin text-[--color-accent]" />
        </Screen>
      }
    >
      <ConfirmedContent />
    </Suspense>
  );
}
