import type { ReactNode } from "react";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Mobile-first shell used by every driver-facing screen. Keeps content
 * within a comfortable phone-width column, centered on larger viewports,
 * so the app reads correctly both on a phone and in a desktop browser.
 */
export function Screen({
  children,
  className,
  bg = "off",
}: {
  children: ReactNode;
  className?: string;
  bg?: "off" | "white";
}) {
  return (
    <div className={cn("min-h-screen w-full", bg === "off" ? "bg-[--color-bg-off]" : "bg-white")}>
      <div className={cn("mx-auto flex min-h-screen w-full max-w-[480px] flex-col bg-white", className)}>
        {children}
      </div>
    </div>
  );
}

export function BackHeader({
  title,
  backHref,
  right,
}: {
  title?: string;
  backHref: string;
  right?: ReactNode;
}) {
  return (
    <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-[--color-border-soft] bg-white/90 px-4 py-3.5 backdrop-blur">
      <Link
        href={backHref}
        aria-label="Go back"
        className="grid h-9 w-9 shrink-0 place-items-center rounded-full text-[--color-navy] transition-colors hover:bg-[--color-bg-off]"
      >
        <ChevronLeft size={22} strokeWidth={2.2} />
      </Link>
      {title && <h1 className="flex-1 truncate text-[15px] font-semibold text-[--color-navy]">{title}</h1>}
      {right && <div className="shrink-0">{right}</div>}
    </header>
  );
}

export function BottomActionBar({ children }: { children: ReactNode }) {
  return (
    <div className="sticky bottom-0 z-30 mt-auto border-t border-[--color-border-soft] bg-white/95 px-4 py-4 backdrop-blur pb-[calc(1rem+env(safe-area-inset-bottom))]">
      {children}
    </div>
  );
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("rounded-2xl border border-[--color-border-soft] bg-white p-4 shadow-soft", className)}>
      {children}
    </div>
  );
}
