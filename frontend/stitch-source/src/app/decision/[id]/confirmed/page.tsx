import Link from "next/link";
import { notFound } from "next/navigation";
import { CalendarClock, CheckCircle2, FileLock2, MapPin } from "lucide-react";
import { getDecisionByLotId } from "@/lib/mock-data";
import { formatRupees, formatShortTime } from "@/lib/utils";
import { Card, Screen } from "@/components/ui/Screen";
import { Button } from "@/components/ui/Button";

export default async function BookingConfirmedPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const decision = getDecisionByLotId(id);
  if (!decision) notFound();

  const bookingRef = `VP-${decision.id.split("-").pop()}`;

  return (
    <Screen className="justify-between px-6 pb-8 pt-14">
      <div className="flex flex-col items-center text-center">
        <span className="grid h-16 w-16 place-items-center rounded-full bg-[--color-teal-50] text-[--color-teal-dark]">
          <CheckCircle2 size={34} strokeWidth={2} />
        </span>
        <h1 className="mt-5 font-serif-display text-2xl font-semibold text-[--color-navy]">Spot confirmed</h1>
        <p className="mt-2 max-w-[280px] text-sm leading-relaxed text-[--color-slate]">
          Your parking is booked. Show your booking reference at the entrance.
        </p>

        <Card className="mt-7 w-full text-left">
          <div className="flex items-center justify-between border-b border-dashed border-[--color-border] pb-3">
            <span className="text-xs font-semibold uppercase tracking-wide text-[--color-slate]">
              Booking reference
            </span>
            <span className="font-mono text-sm font-bold text-[--color-navy]">{bookingRef}</span>
          </div>
          <div className="space-y-3 pt-3">
            <div className="flex items-start gap-2.5">
              <MapPin size={15} className="mt-0.5 shrink-0 text-[--color-navy]" />
              <div>
                <p className="text-[13px] font-semibold text-[--color-charcoal]">{decision.lot.name}</p>
                <p className="text-xs text-[--color-slate]">{decision.lot.address}</p>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <CalendarClock size={15} className="shrink-0 text-[--color-navy]" />
              <p className="text-[13px] text-[--color-charcoal]">
                {formatShortTime(decision.timestamp)} · {decision.durationHours} hours
              </p>
            </div>
            <div className="flex items-center justify-between border-t border-[--color-border-soft] pt-3">
              <span className="text-xs text-[--color-slate]">Amount paid</span>
              <span className="text-base font-bold text-[--color-navy]">{formatRupees(decision.finalPrice)}</span>
            </div>
          </div>
        </Card>

        <Link
          href={`/decision/${id}/audit`}
          className="mt-4 flex items-center gap-2 text-[13px] font-semibold text-[--color-teal-dark]"
        >
          <FileLock2 size={14} /> View audit record for this booking
        </Link>
      </div>

      <div className="space-y-3">
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
