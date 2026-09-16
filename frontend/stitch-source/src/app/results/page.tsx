"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowUpDown, MapPin, ShieldCheck, Sparkles } from "lucide-react";
import { getLots } from "@/lib/mock-data";
import { formatDistance, formatRupees } from "@/lib/utils";
import { BackHeader, Card, Screen } from "@/components/ui/Screen";
import { StatusChip } from "@/components/ui/StatusChip";
import Link from "next/link";

type SortMode = "recommended" | "price" | "distance";

function ResultsSkeleton() {
  return (
    <div className="space-y-3 px-5 pt-4">
      {[0, 1, 2].map((i) => (
        <div key={i} className="animate-pulse-soft rounded-2xl border border-[--color-border-soft] bg-white p-4">
          <div className="h-3 w-2/3 rounded bg-[--color-bg-off]" />
          <div className="mt-3 h-3 w-1/3 rounded bg-[--color-bg-off]" />
          <div className="mt-4 h-6 w-1/4 rounded bg-[--color-bg-off]" />
        </div>
      ))}
    </div>
  );
}

function ResultsContent() {
  const params = useSearchParams();
  const destination = params.get("destination") || "your destination";
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState<SortMode>("recommended");

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 1100);
    return () => clearTimeout(t);
  }, []);

  const lots = useMemo(() => {
    const all = [...getLots()];
    if (sort === "price") return all.sort((a, b) => a.finalPrice - b.finalPrice);
    if (sort === "distance") return all.sort((a, b) => a.distanceMeters - b.distanceMeters);
    return all;
  }, [sort]);

  return (
    <Screen>
      <BackHeader backHref="/search" title={destination} />

      {loading ? (
        <div className="flex-1">
          <div className="flex items-center gap-2 px-5 pt-5 text-sm font-medium text-[--color-teal-dark]">
            <Sparkles size={16} className="animate-pulse-soft" />
            Checking live data for the best spot near you…
          </div>
          <ResultsSkeleton />
        </div>
      ) : (
        <div className="flex-1 px-5 pt-4 pb-8">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-[--color-slate]">{lots.length} verified spots found</p>
            <div className="flex overflow-x-auto no-scrollbar gap-1.5">
              {(["recommended", "price", "distance"] as SortMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setSort(mode)}
                  className={`flex items-center gap-1 whitespace-nowrap rounded-full border px-3 py-1.5 text-xs font-semibold capitalize transition-colors ${
                    sort === mode
                      ? "border-[--color-navy] bg-[--color-navy] text-white"
                      : "border-[--color-border] bg-white text-[--color-charcoal]"
                  }`}
                >
                  {mode === "recommended" && <ArrowUpDown size={11} />}
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {lots.map((lot) => (
              <Link key={lot.id} href={`/decision/${lot.id}`}>
                <Card className="transition-transform active:scale-[0.99]">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-[15px] font-semibold text-[--color-charcoal]">{lot.name}</p>
                      <p className="mt-0.5 flex items-center gap-1 truncate text-xs text-[--color-slate]">
                        <MapPin size={12} /> {formatDistance(lot.distanceMeters)} · {lot.walkMinutes} min walk
                      </p>
                    </div>
                    <StatusChip
                      size="sm"
                      tone={lot.status === "adjusted" ? "adjusted" : "verified"}
                      label={lot.status === "adjusted" ? "Adjusted" : "Verified"}
                      meaning={
                        lot.status === "adjusted"
                          ? "Part of this price couldn't be verified, so it was automatically lowered."
                          : "Every part of this price was checked and confirmed."
                      }
                    />
                  </div>
                  <div className="mt-3 flex items-end justify-between">
                    <div className="flex items-baseline gap-1">
                      <span className="text-2xl font-bold text-[--color-navy]">{formatRupees(lot.finalPrice)}</span>
                      <span className="text-xs text-[--color-slate]">/ 3 hrs</span>
                    </div>
                    <p className="flex items-center gap-1 text-xs text-[--color-slate]">
                      <ShieldCheck size={13} className="text-[--color-teal]" />
                      {lot.spotsAvailable} spots left
                    </p>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      )}
    </Screen>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<ResultsSkeleton />}>
      <ResultsContent />
    </Suspense>
  );
}
