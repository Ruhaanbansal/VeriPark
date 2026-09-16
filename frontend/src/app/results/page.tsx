"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowUpDown, MapPin, ShieldCheck, Sparkles, Star } from "lucide-react";
import { formatDistance, formatRupees } from "@/lib/utils";
import { BackHeader, Card, Screen } from "@/components/ui/Screen";
import { StatusChip } from "@/components/ui/StatusChip";
import Link from "next/link";

import { fetchLots } from "@/lib/api";
import type { ParkingLot } from "@/lib/types";

type SortMode = "recommended" | "price" | "distance";

function ResultsSkeleton() {
  return (
    <div className="space-y-3 px-5 pt-4">
      {[0, 1, 2].map((i) => (
        <div key={i} className="animate-pulse-soft rounded-2xl border border-[--color-border-soft] bg-white p-4">
          <div className="h-24 w-full rounded-xl bg-[--color-bg-off]" />
          <div className="mt-3 h-3 w-2/3 rounded bg-[--color-bg-off]" />
          <div className="mt-2 h-3 w-1/3 rounded bg-[--color-bg-off]" />
          <div className="mt-4 h-6 w-1/4 rounded bg-[--color-bg-off]" />
        </div>
      ))}
    </div>
  );
}

function LotCard({ lot }: { lot: ParkingLot }) {
  // Use decisionId for navigation if available (backend mode),
  // otherwise fall back to lot.id (mock mode — both are handled by fetchDecision).
  const href = `/decision/${lot.decisionId || lot.id}`;

  return (
    <Link href={href}>
      <Card className="overflow-hidden p-0 transition-all hover:border-[--color-accent-200] hover:shadow-soft-lg active:scale-[0.99]">
        {/* Venue visual header */}
        <div className="relative h-24 w-full overflow-hidden bg-[--color-bg-off] border-b border-[--color-border-soft]">
          <VenueImage lotId={lot.id} name={lot.name} coverAsset={lot.coverAsset} />
          {/* Price badge overlay */}
          <div className="absolute bottom-2 right-2 rounded-lg bg-black/60 px-2.5 py-1 backdrop-blur-sm">
            <span className="text-sm font-bold text-white">{formatRupees(lot.finalPrice)}</span>
            {lot.wasAdjusted && lot.originalPrice && lot.originalPrice > lot.finalPrice && (
              <span className="ml-1 text-[10px] text-white/60 line-through">{formatRupees(lot.originalPrice)}</span>
            )}
          </div>
        </div>

        <div className="p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="truncate text-[15px] font-bold text-[--color-charcoal]">{lot.name}</p>
              <p className="mt-0.5 flex items-center gap-1 truncate text-xs text-[--color-slate]">
                <MapPin size={12} className="text-[--color-accent]" />
                {formatDistance(lot.distanceMeters)} · {lot.walkMinutes} min walk
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
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center gap-1 text-xs text-[--color-slate]">
              <Star size={12} className="fill-[--color-amber] text-[--color-amber]" />
              <span className="font-semibold">{lot.rating.toFixed(1)}</span>
            </div>
            <p className="flex items-center gap-1 text-xs font-semibold text-[--color-verified]">
              <ShieldCheck size={13} />
              {lot.spotsAvailable} spots left
            </p>
          </div>
        </div>
      </Card>
    </Link>
  );
}

function VenueImage({ lotId, name, coverAsset }: { lotId: string; name: string; coverAsset?: string }) {
  const cleanLotId = lotId.replace(/^dec-/, "");
  const defaultJpg = `/images/lots/${cleanLotId}.jpg`;
  const initialSrc = coverAsset ? coverAsset.replace(/\.svg$/, ".jpg") : defaultJpg;
  const [src, setSrc] = useState(initialSrc);
  const [failed, setFailed] = useState(false);

  return (
    <div className="relative h-full w-full overflow-hidden bg-slate-100">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={src}
        alt={name}
        className="h-full w-full object-cover transition-transform duration-300 hover:scale-105"
        onError={() => {
          if (!failed) {
            setFailed(true);
            setSrc("/images/lots/lot-metro-hub.jpg");
          }
        }}
      />
    </div>
  );
}

function ResultsContent() {
  const params = useSearchParams();
  const destination = params.get("destination") || "your destination";
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState<SortMode>("recommended");
  const [rawLots, setRawLots] = useState<ParkingLot[]>([]);

  useEffect(() => {
    let isMounted = true;
    fetchLots(destination).then((data) => {
      if (isMounted) {
        setRawLots(data);
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [destination]);

  const lots = useMemo(() => {
    const all = [...rawLots];
    if (sort === "price") return all.sort((a, b) => a.finalPrice - b.finalPrice);
    if (sort === "distance") return all.sort((a, b) => a.distanceMeters - b.distanceMeters);
    return all;
  }, [rawLots, sort]);

  return (
    <Screen>
      <BackHeader backHref="/search" title={destination} />

      {loading ? (
        <div className="flex-1">
          <div className="flex items-center gap-2 px-5 pt-5 text-sm font-medium text-[--color-teal-dark]">
            <Sparkles size={16} className="animate-pulse-soft" />
            VeriCore™ checking live data for the best verified spot near you…
          </div>
          <ResultsSkeleton />
        </div>
      ) : (
        <div className="flex-1 px-5 pt-4 pb-8">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm font-medium text-[--color-slate]">
              {lots.length} verified spot{lots.length !== 1 ? "s" : ""} found
            </p>
            <div className="flex overflow-x-auto no-scrollbar gap-1.5">
              {(["recommended", "price", "distance"] as SortMode[]).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setSort(mode)}
                  className={`flex items-center gap-1 whitespace-nowrap rounded-full border px-3.5 py-1.5 text-xs font-semibold capitalize transition-all duration-150 active:scale-95 ${
                    sort === mode
                      ? "border-amber-600 bg-amber-600 text-white shadow-sm active:bg-amber-700 font-bold"
                      : "border-slate-300 bg-white text-slate-700 hover:border-amber-400 hover:bg-amber-50/50 active:bg-slate-100 font-medium"
                  }`}
                >
                  {mode === "recommended" && <ArrowUpDown size={11} />}
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3.5">
            {lots.map((lot) => (
              <LotCard key={lot.id} lot={lot} />
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
