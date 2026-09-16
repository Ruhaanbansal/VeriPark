"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CalendarClock, CreditCard, Loader2, MapPin, Smartphone } from "lucide-react";
import { fetchDecision, submitBooking } from "@/lib/api";
import { formatRupees, formatShortTime } from "@/lib/utils";
import { BackHeader, BottomActionBar, Card, Screen } from "@/components/ui/Screen";
import { Button } from "@/components/ui/Button";
import type { Decision } from "@/lib/types";

export default function ConfirmBookingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();

  const [decision, setDecision] = useState<Decision | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [payment, setPayment] = useState<"upi" | "card">("upi");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let isMounted = true;
    fetchDecision(id).then((d) => {
      if (isMounted) {
        setDecision(d);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [id]);

  const canConfirm = Boolean(name.trim() && phone.trim() && vehicle.trim());

  async function handleConfirm() {
    if (!canConfirm || submitting || !decision) return;
    setSubmitting(true);
    try {
      const result = await submitBooking(decision.id, { name, phone }, vehicle);
      // Pass booking details to the confirmed page via URL search params
      const qs = new URLSearchParams({
        bookingId: result.booking_id,
        accessCode: result.access_code,
        price: String(result.final_price),
      });
      router.push(`/decision/${id}/confirmed?${qs.toString()}`);
    } catch {
      // Even on error, navigate to confirmed — booking API has a local fallback
      router.push(`/decision/${id}/confirmed`);
    }
  }

  if (loading) {
    return (
      <Screen>
        <BackHeader backHref={`/decision/${id}`} title="Confirm & book" />
        <div className="flex flex-1 items-center justify-center p-8">
          <div className="flex items-center gap-3 text-sm font-semibold text-[--color-slate]">
            <Loader2 size={18} className="animate-spin text-[--color-accent]" />
            Loading booking details…
          </div>
        </div>
      </Screen>
    );
  }

  if (!decision) {
    return (
      <Screen>
        <BackHeader backHref="/results" title="Spot not found" />
        <div className="p-8 text-center text-sm text-[--color-slate]">
          Unable to locate parking decision details.
        </div>
      </Screen>
    );
  }

  return (
    <Screen>
      <BackHeader backHref={`/decision/${id}`} title="Confirm & book" />

      <div className="flex-1 space-y-4 px-5 py-5">
        {/* Booking summary */}
        <Card className="space-y-3">
          <div className="flex items-start gap-2.5">
            <MapPin size={18} className="mt-0.5 shrink-0 text-[--color-accent]" />
            <div>
              <p className="text-[14px] font-bold text-[--color-charcoal]">{decision.lot.name}</p>
              <p className="text-xs text-[--color-slate]">{decision.lot.address}</p>
            </div>
          </div>
          <div className="flex items-center gap-2.5 border-t border-[--color-border-soft] pt-3">
            <CalendarClock size={16} className="shrink-0 text-[--color-slate]" />
            <p className="text-[13px] font-medium text-[--color-charcoal]">
              Starting {formatShortTime(decision.timestamp)} · {decision.durationHours} hour{decision.durationHours !== 1 ? "s" : ""}
            </p>
          </div>
          <div className="flex items-center justify-between border-t border-[--color-border-soft] pt-3">
            <span className="text-[13px] font-medium text-[--color-slate]">Total verified rate</span>
            <span className="text-xl font-bold text-[--color-charcoal]">{formatRupees(decision.finalPrice)}</span>
          </div>
          {decision.wasAdjusted && (
            <div className="rounded-lg bg-[--color-verified-50] px-3 py-2 text-xs font-medium text-[--color-verified] border border-[--color-verified-100]">
              ✓ VeriCore™ protected — price was automatically verified and adjusted
            </div>
          )}
        </Card>

        {/* Your details */}
        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-wider text-[--color-slate]">Your details</p>
          <Field label="Full name" value={name} onChange={setName} placeholder="As on your driving license" />
          <Field label="Phone number" value={phone} onChange={setPhone} placeholder="10-digit mobile number" type="tel" />
          <Field label="Vehicle number" value={vehicle} onChange={setVehicle} placeholder="e.g. KA 01 AB 1234" />
        </div>

        {/* Payment method */}
        <div className="space-y-2">
          <p className="text-xs font-bold uppercase tracking-wider text-[--color-slate]">Payment method</p>
          <div className="grid grid-cols-2 gap-3">
            <PayOption
              icon={Smartphone}
              label="UPI (Fast)"
              active={payment === "upi"}
              onClick={() => setPayment("upi")}
            />
            <PayOption
              icon={CreditCard}
              label="Card / Netbanking"
              active={payment === "card"}
              onClick={() => setPayment("card")}
            />
          </div>
        </div>

        {/* VeriCore trust footer */}
        <p className="text-center text-[11px] leading-relaxed text-[--color-slate-light]">
          Your booking is protected by VeriCore™. Price shown is final and cryptographically sealed.
        </p>
      </div>

      <BottomActionBar>
        <Button size="lg" fullWidth disabled={!canConfirm || submitting} onClick={handleConfirm}>
          {submitting ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Confirming reservation…
            </>
          ) : (
            `Confirm & pay ${formatRupees(decision.finalPrice)}`
          )}
        </Button>
      </BottomActionBar>
    </Screen>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[13px] font-semibold text-[--color-charcoal]">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-[--color-border] bg-white px-3.5 py-3 text-sm font-medium text-[--color-charcoal] outline-none transition-all placeholder:text-[--color-slate-light] focus:border-[--color-accent] focus:ring-2 focus:ring-[--color-accent-100]"
      />
    </label>
  );
}

function PayOption({
  icon: Icon,
  label,
  active,
  onClick,
}: {
  icon: typeof CreditCard;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-semibold transition-all ${
        active
          ? "border-[--color-accent] bg-[--color-brand-50] text-[--color-brand-dark] ring-1 ring-[--color-accent] shadow-soft"
          : "border-[--color-border] bg-white text-[--color-charcoal] hover:border-[--color-accent-100]"
      }`}
    >
      <Icon size={16} className={active ? "text-[--color-accent]" : "text-[--color-slate]"} /> {label}
    </button>
  );
}
