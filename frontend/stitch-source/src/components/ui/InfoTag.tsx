"use client";

import { Info } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

/**
 * A small inline icon that reveals a one-line, plain-language meaning
 * on tap (mobile) or hover (desktop). Used to satisfy the rule that no
 * icon anywhere in VeriPark should be a mystery.
 */
export function InfoTag({ meaning, className }: { meaning: string; className?: string }) {
  const [open, setOpen] = useState(false);

  return (
    <span className={cn("group relative inline-flex", className)}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        onBlur={() => setOpen(false)}
        className="grid h-5 w-5 place-items-center rounded-full text-[--color-slate-light] transition-colors hover:bg-[--color-bg-off] hover:text-[--color-slate]"
        aria-label={meaning}
      >
        <Info size={14} strokeWidth={2.2} />
      </button>
      <span
        role="tooltip"
        className={cn(
          "pointer-events-none absolute left-1/2 top-full z-30 mt-2 w-48 -translate-x-1/2 rounded-lg border border-[--color-border-soft] bg-[--color-navy] p-2.5 text-[11px] leading-snug text-white opacity-0 shadow-soft-lg transition-opacity duration-150",
          "group-hover:opacity-100",
          open && "opacity-100",
        )}
      >
        {meaning}
      </span>
    </span>
  );
}
