import Link from "next/link";
import { MapPinned, Receipt, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Logo } from "@/components/ui/Logo";
import { Screen } from "@/components/ui/Screen";

const STEPS = [
  {
    icon: MapPinned,
    title: "We find your spot",
    description: "Ranked by distance, availability, and verified price.",
    tone: "amber",
  },
  {
    icon: Receipt,
    title: "We show you why it costs what it costs",
    description: "A plain-language reason, not just a number.",
    tone: "emerald",
  },
  {
    icon: ShieldCheck,
    title: "We verify the reason is real",
    description: "Checked claim by claim before you ever see it.",
    tone: "blue",
  },
];

const STEP_ICON_BG: Record<string, string> = {
  amber:   "bg-[--color-amber-50]   text-[--color-amber-dark]",
  emerald: "bg-[--color-verified-50] text-[--color-verified]",
  blue:    "bg-[--color-live-50]    text-[--color-live]",
};

export default function OnboardingPage() {
  return (
    <Screen className="justify-between px-6 pb-8 pt-7">
      <div className="flex flex-col items-center text-center">
        <Logo size="md" className="self-start animate-fade-in" />

        {/* Hero Illustration — inline SVG, no broken image dependency */}
        <div className="relative mt-5 h-[210px] w-full max-w-[360px] overflow-hidden rounded-[--radius-2xl] bg-gradient-to-br from-[#fef3c7] via-[#fefce8] to-[#ecfdf5] shadow-soft animate-fade-in">
          <svg
            viewBox="0 0 360 210"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="absolute inset-0 h-full w-full"
          >
            {/* Grid lines */}
            <line x1="0" y1="70" x2="360" y2="70" stroke="#e2d9cc" strokeWidth="1"/>
            <line x1="0" y1="140" x2="360" y2="140" stroke="#e2d9cc" strokeWidth="1"/>
            <line x1="90" y1="0" x2="90" y2="210" stroke="#e2d9cc" strokeWidth="1"/>
            <line x1="180" y1="0" x2="180" y2="210" stroke="#e2d9cc" strokeWidth="1"/>
            <line x1="270" y1="0" x2="270" y2="210" stroke="#e2d9cc" strokeWidth="1"/>
            {/* Parking bays */}
            <rect x="20"  y="20"  width="52" height="32" rx="5" fill="#fef3c7" stroke="#fde68a" strokeWidth="1.5"/>
            <rect x="82"  y="20"  width="52" height="32" rx="5" fill="#d1fae5" stroke="#a7f3d0" strokeWidth="1.5"/>
            <rect x="144" y="20"  width="52" height="32" rx="5" fill="#fef3c7" stroke="#fde68a" strokeWidth="1.5"/>
            <rect x="206" y="20"  width="52" height="32" rx="5" fill="#dbeafe" stroke="#bfdbfe" strokeWidth="1.5"/>
            <rect x="268" y="20"  width="52" height="32" rx="5" fill="#fef3c7" stroke="#fde68a" strokeWidth="1.5"/>
            {/* Car shapes in bays */}
            <rect x="29"  y="27" width="34" height="18" rx="4" fill="#d97706" opacity="0.9"/>
            <rect x="91"  y="27" width="34" height="18" rx="4" fill="#059669" opacity="0.85"/>
            <rect x="215" y="27" width="34" height="18" rx="4" fill="#3b82f6" opacity="0.8"/>
            <rect x="277" y="27" width="34" height="18" rx="4" fill="#d97706" opacity="0.7"/>
            {/* Lower tier */}
            <rect x="20"  y="80"  width="52" height="32" rx="5" fill="#fef3c7" stroke="#fde68a" strokeWidth="1.5"/>
            <rect x="82"  y="80"  width="52" height="32" rx="5" fill="#fef3c7" stroke="#fde68a" strokeWidth="1.5"/>
            <rect x="144" y="80"  width="52" height="32" rx="5" fill="#d1fae5" stroke="#a7f3d0" strokeWidth="1.5"/>
            <rect x="206" y="80"  width="52" height="32" rx="5" fill="#fef3c7" stroke="#fde68a" strokeWidth="1.5"/>
            <rect x="268" y="80"  width="52" height="32" rx="5" fill="#fef3c7" stroke="#fde68a" strokeWidth="1.5"/>
            <rect x="29"  y="87" width="34" height="18" rx="4" fill="#b45309" opacity="0.8"/>
            <rect x="91"  y="87" width="34" height="18" rx="4" fill="#d97706" opacity="0.7"/>
            <rect x="277" y="87" width="34" height="18" rx="4" fill="#92400e" opacity="0.75"/>
            {/* VeriCore badge */}
            <circle cx="180" cy="155" r="35" fill="white" opacity="0.95" filter="url(#blur1)"/>
            <circle cx="180" cy="155" r="28" fill="#d97706" opacity="0.12"/>
            <circle cx="180" cy="155" r="20" fill="#d97706" opacity="0.18"/>
            {/* Shield icon */}
            <path d="M180 139 L191 143.5 V152.5 C191 159 186 164.5 180 167 C174 164.5 169 159 169 152.5 V143.5 Z" fill="#d97706" opacity="0.9"/>
            <path d="M175 153.5 L178.5 157 L185.5 149.5" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
            {/* Sparkle dots */}
            <circle cx="135" cy="155" r="4" fill="#d97706" opacity="0.6"/>
            <circle cx="120" cy="145" r="2.5" fill="#d97706" opacity="0.4"/>
            <circle cx="225" cy="155" r="4" fill="#059669" opacity="0.6"/>
            <circle cx="240" cy="145" r="2.5" fill="#059669" opacity="0.4"/>
            <defs>
              <filter id="blur1" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="6"/>
              </filter>
            </defs>
          </svg>
        </div>

        <h1 className="mt-6 font-serif-display text-[27px] font-semibold leading-[1.2] text-[--color-charcoal] animate-fade-in-up">
          Every price, explained{" "}
          <span className="text-[--color-accent]">and verified</span> — before you pay.
        </h1>
        <p className="mt-3 max-w-[300px] text-[15px] leading-relaxed text-[--color-slate] animate-fade-in-up delay-75">
          VeriPark checks its own reasoning against real evidence every time — so the price you see is one you can trust.
        </p>
      </div>

      <div className="mt-7 space-y-2.5">
        {STEPS.map((step, i) => (
          <div
            key={step.title}
            className={`flex items-center gap-3.5 rounded-2xl border border-[--color-border-soft] bg-white p-3.5 shadow-soft animate-fade-in-up`}
            style={{ animationDelay: `${(i + 2) * 80}ms` }}
          >
            <span className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl ${STEP_ICON_BG[step.tone]}`}>
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

      <div className="mt-7 space-y-3">
        <Button href="/search" size="lg" fullWidth>
          Find Parking
        </Button>
        <div className="flex items-center justify-center gap-4 pt-1">
          <Link
            href="/how-it-works"
            className="text-[13px] font-semibold text-[--color-accent-dark] underline decoration-[--color-accent-200] underline-offset-4 hover:text-[--color-accent] transition-colors"
          >
            How it works
          </Link>
          <span className="text-[--color-border]">•</span>
          <Link
            href="/operator"
            className="text-[13px] font-medium text-[--color-slate] underline decoration-[--color-border] underline-offset-4 hover:text-[--color-charcoal] transition-colors"
          >
            For Operators
          </Link>
        </div>
      </div>
    </Screen>
  );
}

