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
          "grid shrink-0 place-items-center rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 text-white shadow-md shadow-amber-600/30",
          dims,
        )}
      >
        <ShieldCheck size={iconDims} strokeWidth={2.5} className="text-white drop-shadow-sm" />
      </span>
      <span className={cn("font-serif-display font-bold tracking-tight text-slate-900", text)}>
        VeriPark
      </span>
    </div>
  );
}
