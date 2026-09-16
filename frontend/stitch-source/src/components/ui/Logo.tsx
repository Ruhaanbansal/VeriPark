import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

export function Logo({ size = "md", className }: { size?: "sm" | "md" | "lg"; className?: string }) {
  const dims = size === "lg" ? "h-11 w-11" : size === "sm" ? "h-7 w-7" : "h-9 w-9";
  const iconDims = size === "lg" ? 22 : size === "sm" ? 15 : 18;
  const text = size === "lg" ? "text-2xl" : size === "sm" ? "text-base" : "text-lg";

  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <span
        className={cn(
          "grid shrink-0 place-items-center rounded-xl bg-[--color-navy] text-white shadow-soft",
          dims,
        )}
      >
        <ShieldCheck size={iconDims} strokeWidth={2.25} />
      </span>
      <span className={cn("font-serif-display font-semibold tracking-tight text-[--color-navy]", text)}>
        VeriPark
      </span>
    </div>
  );
}
