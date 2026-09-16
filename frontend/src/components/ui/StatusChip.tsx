"use client";

import { CheckCircle2, Radar, MinusCircle, AlertCircle } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

export type ChipTone = "verified" | "adjusted" | "live" | "excluded" | "neutral";

const TONE_STYLES: Record<ChipTone, string> = {
  verified:  "bg-[--color-verified-50]  text-[--color-verified]  border-[--color-verified-100]",
  adjusted:  "bg-[--color-adjusted-50]  text-[--color-adjusted]  border-[--color-adjusted-100]",
  live:      "bg-[--color-live-50]       text-[--color-live]       border-[--color-live-100]",
  excluded:  "bg-[--color-slate-100]    text-[--color-slate]      border-[--color-border-soft]",
  neutral:   "bg-[--color-bg-off]       text-[--color-slate]      border-[--color-border-soft]",
};

const TONE_ICON: Record<ChipTone, React.ComponentType<{ size?: number; strokeWidth?: number }>> = {
  verified: CheckCircle2,
  adjusted: AlertCircle,
  live: Radar,
  excluded: MinusCircle,
  neutral: MinusCircle,
};

export function StatusChip({
  tone,
  label,
  meaning,
  size = "md",
}: {
  tone: ChipTone;
  label: string;
  meaning?: string;
  size?: "sm" | "md";
}) {
  const [open, setOpen] = useState(false);
  const Icon = TONE_ICON[tone];

  return (
    <span className="relative inline-flex">
      <button
        type="button"
        onClick={() => meaning && setOpen((v) => !v)}
        onBlur={() => setOpen(false)}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full border font-semibold",
          TONE_STYLES[tone],
          size === "sm" ? "px-2.5 py-1 text-xs" : "px-3 py-1.5 text-[13px]",
          meaning && "cursor-help",
        )}
        aria-label={meaning ? `${label}: ${meaning}` : label}
      >
        <Icon size={size === "sm" ? 13 : 15} strokeWidth={2.4} />
        {label}
      </button>
      {open && meaning && (
        <span
          role="tooltip"
          className="absolute left-1/2 top-full z-20 mt-2 w-52 -translate-x-1/2 rounded-xl border border-[--color-border-soft] bg-white p-3 text-xs leading-relaxed text-[--color-charcoal] shadow-soft-lg animate-fade-in-up"
        >
          {meaning}
        </span>
      )}
    </span>
  );
}
