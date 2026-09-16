import Image from "next/image";
import Link from "next/link";
import { MapPinned, Receipt, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";
import { Screen } from "@/components/ui/Screen";

const STEPS = [
  {
    icon: MapPinned,
    title: "We find your spot",
    description: "Ranked by distance, availability, and price.",
  },
  {
    icon: Receipt,
    title: "We show you why it costs what it costs",
    description: "A plain-language reason, not just a number.",
  },
  {
    icon: ShieldCheck,
    title: "We verify the reason is real",
    description: "Checked claim by claim before you ever see it.",
  },
];

export default function OnboardingPage() {
  return (
    <Screen className="justify-between px-6 pb-8 pt-7">
      <div className="flex flex-col items-center text-center">
        <Logo size="md" className="self-start" />

        <div className="relative mt-4 h-[220px] w-full max-w-[340px] overflow-hidden rounded-[--radius-2xl]">
          <Image
            src="/images/onboarding-hero.png"
            alt=""
            fill
            priority
            className="object-cover"
            sizes="340px"
          />
        </div>

        <h1 className="mt-7 font-serif-display text-[28px] font-semibold leading-[1.2] text-[--color-navy]">
          Every price, explained and verified — before you pay.
        </h1>
        <p className="mt-3 max-w-[320px] text-[15px] leading-relaxed text-[--color-slate]">
          VeriPark checks its own reasoning against real evidence, every time — so the price you see is one you can trust.
        </p>
      </div>

      <div className="mt-8 space-y-3">
        {STEPS.map((step, i) => (
          <div
            key={step.title}
            className="flex items-center gap-3.5 rounded-2xl border border-[--color-border-soft] bg-white p-3.5 shadow-soft"
          >
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-[--color-navy-50] text-[--color-navy]">
              <step.icon size={20} strokeWidth={2} />
            </span>
            <div className="min-w-0">
              <p className="text-[13px] font-semibold text-[--color-charcoal]">
                {i + 1}. {step.title}
              </p>
              <p className="truncate text-xs text-[--color-slate]">{step.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 space-y-3">
        <Button href="/search" size="lg" fullWidth>
          Find Parking
        </Button>
        <div className="flex items-center justify-center gap-4 pt-1">
          <Link
            href="/how-it-works"
            className="text-[13px] font-semibold text-[--color-teal-dark] underline decoration-[--color-teal-100] underline-offset-4"
          >
            How it works
          </Link>
          <span className="text-[--color-border]">•</span>
          <Link
            href="/operator"
            className="text-[13px] font-medium text-[--color-slate] underline decoration-[--color-border] underline-offset-4"
          >
            For Operators
          </Link>
        </div>
      </div>
    </Screen>
  );
}
