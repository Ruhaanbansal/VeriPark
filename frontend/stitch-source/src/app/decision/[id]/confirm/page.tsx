"use client";

import { use, useState } from "react";
import { notFound, useRouter } from "next/navigation";
import { CalendarClock, CreditCard, MapPin, Smartphone } from "lucide-react";
import { getDecisionByLotId } from "@/lib/mock-data";
import { formatRupees, formatShortTime } from "@/lib/utils";
import { BackHeader, BottomActionBar, Card, Screen } from "@/components/ui/Screen";
import { Button } from "@/components/ui/Button";

export default function ConfirmBookingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const decision = getDecisionByLotId(id);
  const router = useRouter();

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [payment, setPayment] = useState<"upi" | "card">("upi");
  const [submitting, setSubmitting] = useState(false);

  if (!decision) notFound();

  const canConfirm = name.trim() && phone.trim() && vehicle.trim();

  function handleConfirm() {
    if (!canConfirm || submitting) return;
    setSubmitting(true);
    setTimeout(() => {
      router.push(`/decision/${id}/confirmed`);
    }, 900);
  }

  return (
    <Screen>
      <BackHeader backHref={`/decision/${id}`} title="Confirm & book" />

      <div className="flex-1 space-y-4 px-5 py-5">
        <Card className="space-y-3">
          <div className="flex items-start gap-2.5">
            <MapPin size={16} className="mt-0.5 shrink-0 text-[--color-navy]" />
            <div>
              <p className="text-[14px] font-semibold text-[--color-charcoal]">{decision.lot.name}</p>
              <p className="text-xs text-[--color-slate]">{decision.lot.address}</p>
            </div>
          </div>
          <div className="flex items-center gap-2.5 border-t border-[--color-border-soft] pt-3">
            <CalendarClock size={16} className="shrink-0 text-[--color-navy]" />
            <p className="text-[13px] text-[--color-charcoal]">
              Starting {formatShortTime(decision.timestamp)} · {decision.durationHours} hours
            </p>
          </div>
          <div className="flex items-center justify-between border-t border-[--color-border-soft] pt-3">
            <span className="text-[13px] text-[--color-slate]">Total</span>
            <span className="text-lg font-bold text-[--color-navy]">{formatRupees(decision.finalPrice)}</span>
          </div>
        </Card>

        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-[--color-slate]">Your details</p>
          <Field label="Full name" value={name} onChange={setName} placeholder="As on your ID" />
          <Field label="Phone number" value={phone} onChange={setPhone} placeholder="10-digit mobile number" />
          <Field label="Vehicle number" value={vehicle} onChange={setVehicle} placeholder="e.g. KA 01 AB 1234" />
        </div>

        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-[--color-slate]">Payment method</p>
          <div className="grid grid-cols-2 gap-3">
            <PayOption
              icon={Smartphone}
              label="UPI"
              active={payment === "upi"}
              onClick={() => setPayment("upi")}
            />
            <PayOption
              icon={CreditCard}
              label="Card"
              active={payment === "card"}
              onClick={() => setPayment("card")}
            />
          </div>
        </div>
      </div>

      <BottomActionBar>
        <Button size="lg" fullWidth disabled={!canConfirm || submitting} onClick={handleConfirm}>
          {submitting ? "Confirming…" : `Confirm & pay ${formatRupees(decision.finalPrice)}`}
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
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[13px] font-medium text-[--color-charcoal]">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-[--color-border] bg-white px-3.5 py-3 text-sm text-[--color-charcoal] outline-none focus:border-[--color-teal] focus:ring-2 focus:ring-[--color-teal-100]"
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
      onClick={onClick}
      className={`flex items-center justify-center gap-2 rounded-xl border px-4 py-3 text-sm font-semibold transition-colors ${
        active
          ? "border-[--color-navy] bg-[--color-navy-50] text-[--color-navy]"
          : "border-[--color-border] bg-white text-[--color-charcoal]"
      }`}
    >
      <Icon size={16} /> {label}
    </button>
  );
}
