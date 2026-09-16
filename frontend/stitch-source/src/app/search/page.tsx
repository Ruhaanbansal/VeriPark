"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Clock, MapPin, Navigation, Search as SearchIcon } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { BackHeader, BottomActionBar, Screen } from "@/components/ui/Screen";

const TIME_OPTIONS = ["Now", "In 15 min", "In 30 min", "Choose time"] as const;

const RECENTS = ["MG Road, Bengaluru", "Kempegowda International Airport", "Brigade Road"];

export default function SearchPage() {
  const router = useRouter();
  const [destination, setDestination] = useState("");
  const [when, setWhen] = useState<(typeof TIME_OPTIONS)[number]>("Now");
  const [customTime, setCustomTime] = useState("");

  const canSearch = useMemo(() => destination.trim().length > 0, [destination]);

  function handleSearch(dest?: string) {
    const finalDest = dest ?? destination;
    if (!finalDest.trim()) return;
    const params = new URLSearchParams({ destination: finalDest, when });
    router.push(`/results?${params.toString()}`);
  }

  return (
    <Screen>
      <BackHeader backHref="/" />
      <div className="flex-1 px-5 pt-3">
        {/* Decorative map motif */}
        <div className="relative mb-6 h-32 w-full overflow-hidden rounded-2xl bg-[--color-navy-50]">
          <svg
            className="absolute inset-0 h-full w-full opacity-70"
            viewBox="0 0 400 130"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M0 40 H400" stroke="#c9d6e0" strokeWidth="1.5" />
            <path d="M0 90 H400" stroke="#c9d6e0" strokeWidth="1.5" />
            <path d="M90 0 V130" stroke="#c9d6e0" strokeWidth="1.5" />
            <path d="M250 0 V130" stroke="#c9d6e0" strokeWidth="1.5" />
            <path d="M320 0 V130" stroke="#c9d6e0" strokeWidth="1.5" />
            <circle cx="250" cy="40" r="5" fill="#2E7D6B" />
            <circle cx="250" cy="40" r="10" fill="#2E7D6B" fillOpacity="0.25" />
          </svg>
          <div className="absolute inset-0 grid place-items-center">
            <span className="grid h-11 w-11 place-items-center rounded-full bg-white shadow-soft-lg text-[--color-teal-dark]">
              <Navigation size={20} strokeWidth={2.2} />
            </span>
          </div>
        </div>

        <h1 className="font-serif-display text-2xl font-semibold text-[--color-navy]">Where are you headed?</h1>
        <p className="mt-1.5 text-sm text-[--color-slate]">We&apos;ll find verified spots nearby.</p>

        <div className="mt-5 flex items-center gap-3 rounded-2xl border border-[--color-border] bg-white px-4 py-3.5 shadow-soft focus-within:border-[--color-teal] focus-within:ring-2 focus-within:ring-[--color-teal-100]">
          <SearchIcon size={19} className="shrink-0 text-[--color-slate-light]" />
          <input
            autoFocus
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Address, landmark, or area"
            className="w-full bg-transparent text-[15px] text-[--color-charcoal] outline-none placeholder:text-[--color-slate-light]"
          />
        </div>

        <div className="mt-5">
          <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-[--color-slate]">
            <Clock size={13} /> When
          </p>
          <div className="flex flex-wrap gap-2">
            {TIME_OPTIONS.map((option) => (
              <button
                key={option}
                onClick={() => setWhen(option)}
                className={`rounded-full border px-3.5 py-2 text-[13px] font-semibold transition-colors ${
                  when === option
                    ? "border-[--color-navy] bg-[--color-navy] text-white"
                    : "border-[--color-border] bg-white text-[--color-charcoal] hover:border-[--color-navy-50]"
                }`}
              >
                {option}
              </button>
            ))}
          </div>
          {when === "Choose time" && (
            <input
              type="datetime-local"
              value={customTime}
              onChange={(e) => setCustomTime(e.target.value)}
              className="mt-3 w-full rounded-xl border border-[--color-border] bg-white px-3.5 py-2.5 text-sm text-[--color-charcoal] outline-none focus:border-[--color-teal]"
            />
          )}
        </div>

        <div className="mt-6">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[--color-slate]">Recent</p>
          <div className="space-y-1">
            {RECENTS.map((place) => (
              <button
                key={place}
                onClick={() => {
                  setDestination(place);
                  handleSearch(place);
                }}
                className="flex w-full items-center gap-3 rounded-xl px-2 py-2.5 text-left transition-colors hover:bg-[--color-bg-off]"
              >
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-[--color-bg-off] text-[--color-slate]">
                  <MapPin size={15} />
                </span>
                <span className="truncate text-sm text-[--color-charcoal]">{place}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <BottomActionBar>
        <Button size="lg" fullWidth disabled={!canSearch} onClick={() => handleSearch()}>
          Find Parking
        </Button>
      </BottomActionBar>
    </Screen>
  );
}
