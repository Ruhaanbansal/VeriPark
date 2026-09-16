"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Clock, MapPin, Navigation, Search as SearchIcon, X, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { BackHeader, BottomActionBar, Screen } from "@/components/ui/Screen";

const TIME_OPTIONS = ["Now", "In 15 min", "In 30 min", "Choose time"] as const;

interface LocationOption {
  title: string;
  subtitle: string;
  zone: string;
  spots: number;
}

const SEARCH_SUGGESTIONS: LocationOption[] = [
  { title: "MG Road, Bengaluru", subtitle: "Metro Station & Brigade Rd Junction", zone: "Central Core", spots: 14 },
  { title: "Kempegowda International Airport", subtitle: "Terminal 1 & 2 Multi-Level Decks", zone: "North / Airport", spots: 85 },
  { title: "Brigade Road", subtitle: "Commercial & Retail Shopping Hub", zone: "Central Core", spots: 22 },
  { title: "Indiranagar 100ft Road", subtitle: "Near HAL 2nd Stage Dining Corridor", zone: "East Corridor", spots: 14 },
  { title: "Prestige Commercial Plaza Deck", subtitle: "Residency Road Commercial Zone", zone: "Central Core", spots: 46 },
  { title: "Town Hall Civic Underground", subtitle: "JC Road Civic & Cultural Center", zone: "Central Core", spots: 72 },
  { title: "Manipal Hospital", subtitle: "Old Airport Road OPD & Emergency", zone: "East Corridor", spots: 18 },
  { title: "Koramangala 4th Block", subtitle: "80 Feet Road & Nexus Transit Plaza", zone: "South Core", spots: 110 },
  { title: "Richmond Circle Automated Deck", subtitle: "Richmond Rd Flyover Entrance", zone: "Central Core", spots: 28 },
  { title: "UB City / Vittal Mallya Road", subtitle: "Luxury Mall & Commercial Towers", zone: "Central Core", spots: 35 },
  { title: "Whitefield ITPL", subtitle: "International Tech Park Main Road", zone: "Tech Corridor", spots: 50 },
  { title: "Electronic City Phase 1", subtitle: "Hosur Road & Infosys Gateway", zone: "South Corridor", spots: 64 },
  { title: "Church Street", subtitle: "Pedestrian Strip & Cafe Quarter", zone: "Central Core", spots: 12 },
  { title: "Cubbon Park / High Court", subtitle: "Kasturba Road Entrance", zone: "Central Core", spots: 40 },
  { title: "Jayanagar 4th Block", subtitle: "BDA Shopping Complex", zone: "South Core", spots: 30 },
];

const RECENTS = [
  "MG Road, Bengaluru",
  "Kempegowda International Airport",
  "Brigade Road",
];

export default function SearchPage() {
  const router = useRouter();
  const [destination, setDestination] = useState("");
  const [when, setWhen] = useState<(typeof TIME_OPTIONS)[number]>("Now");
  const [customTime, setCustomTime] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const canSearch = useMemo(() => destination.trim().length > 0, [destination]);

  // Filtered suggestions based on user typing
  const filteredSuggestions = useMemo(() => {
    const q = destination.trim().toLowerCase();
    if (!q) return SEARCH_SUGGESTIONS.slice(0, 6);
    return SEARCH_SUGGESTIONS.filter(
      (loc) =>
        loc.title.toLowerCase().includes(q) ||
        loc.subtitle.toLowerCase().includes(q) ||
        loc.zone.toLowerCase().includes(q)
    );
  }, [destination]);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleSearch(dest?: string) {
    const finalDest = dest ?? destination;
    if (!finalDest.trim()) return;
    setIsDropdownOpen(false);
    const params = new URLSearchParams({ destination: finalDest.trim(), when });
    router.push(`/results?${params.toString()}`);
  }

  function handleSelectSuggestion(loc: LocationOption) {
    setDestination(loc.title);
    setIsDropdownOpen(false);
    handleSearch(loc.title);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!isDropdownOpen && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
      setIsDropdownOpen(true);
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < filteredSuggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : filteredSuggestions.length - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (selectedIndex >= 0 && selectedIndex < filteredSuggestions.length) {
        handleSelectSuggestion(filteredSuggestions[selectedIndex]);
      } else {
        handleSearch();
      }
    } else if (e.key === "Escape") {
      setIsDropdownOpen(false);
    }
  }

  return (
    <Screen>
      <BackHeader backHref="/" />
      <div className="flex-1 px-5 pt-3">
        {/* Decorative map motif */}
        <div className="relative mb-5 h-28 w-full overflow-hidden rounded-2xl bg-amber-50 border border-amber-100">
          <svg
            className="absolute inset-0 h-full w-full opacity-70"
            viewBox="0 0 400 130"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M0 40 H400" stroke="#fde68a" strokeWidth="1.5" />
            <path d="M0 90 H400" stroke="#fde68a" strokeWidth="1.5" />
            <path d="M90 0 V130" stroke="#fde68a" strokeWidth="1.5" />
            <path d="M250 0 V130" stroke="#fde68a" strokeWidth="1.5" />
            <path d="M320 0 V130" stroke="#fde68a" strokeWidth="1.5" />
            <circle cx="250" cy="40" r="5" fill="#d97706" />
            <circle cx="250" cy="40" r="14" fill="#d97706" fillOpacity="0.18" />
            <circle cx="90" cy="90" r="3" fill="#059669" opacity="0.6" />
            <circle cx="90" cy="90" r="8" fill="#059669" fillOpacity="0.15" />
          </svg>
          <div className="absolute inset-0 grid place-items-center">
            <span className="grid h-11 w-11 place-items-center rounded-full bg-white shadow-md shadow-amber-600/20 text-amber-600 border border-amber-200">
              <Navigation size={20} strokeWidth={2.4} />
            </span>
          </div>
        </div>

        <h1 className="font-serif-display text-2xl font-bold text-slate-900">Where are you headed?</h1>
        <p className="mt-1 text-sm text-slate-600">We&apos;ll find verified spots nearby with real-time pricing.</p>

        {/* Search Input Container with Dropdown Suggestions */}
        <div ref={containerRef} className="relative mt-5">
          <div
            className={`flex items-center gap-3 rounded-2xl border bg-white px-4 py-3.5 shadow-sm transition-all duration-150 ${
              isDropdownOpen
                ? "border-amber-600 ring-2 ring-amber-500/20"
                : "border-slate-300 hover:border-slate-400"
            }`}
          >
            <SearchIcon size={19} className="shrink-0 text-amber-600" />
            <input
              ref={inputRef}
              autoFocus
              value={destination}
              onChange={(e) => {
                setDestination(e.target.value);
                setIsDropdownOpen(true);
                setSelectedIndex(-1);
              }}
              onFocus={() => setIsDropdownOpen(true)}
              onKeyDown={handleKeyDown}
              placeholder="Address, landmark, or area (e.g. MG Road, Airport)"
              className="w-full bg-transparent text-[15px] font-medium text-slate-900 outline-none placeholder:text-slate-400"
            />
            {destination && (
              <button
                type="button"
                onClick={() => {
                  setDestination("");
                  inputRef.current?.focus();
                }}
                className="grid h-6 w-6 shrink-0 place-items-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              >
                <X size={15} />
              </button>
            )}
          </div>

          {/* Autocomplete Dropdown Panel */}
          {isDropdownOpen && (
            <div className="absolute left-0 right-0 top-full z-50 mt-2 max-h-72 overflow-y-auto rounded-2xl border border-slate-200 bg-white py-2 shadow-xl animate-fade-in">
              <div className="px-3 py-1.5 flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-100">
                <span>{destination.trim() ? "Matching Locations" : "Suggested Locations"}</span>
                <span className="text-amber-700 flex items-center gap-1 font-semibold">
                  <Sparkles size={11} /> VeriCore Live
                </span>
              </div>

              {filteredSuggestions.length === 0 ? (
                <div className="px-4 py-6 text-center text-sm text-slate-500">
                  <p>No matching parking locations found for &ldquo;{destination}&rdquo;</p>
                  <button
                    type="button"
                    onClick={() => handleSearch()}
                    className="mt-2 text-xs font-semibold text-amber-700 underline"
                  >
                    Search anyway
                  </button>
                </div>
              ) : (
                filteredSuggestions.map((loc, idx) => {
                  const isSelected = idx === selectedIndex;
                  return (
                    <button
                      key={loc.title}
                      type="button"
                      onClick={() => handleSelectSuggestion(loc)}
                      onMouseEnter={() => setSelectedIndex(idx)}
                      className={`flex w-full items-center gap-3 px-3.5 py-2.5 text-left transition-colors ${
                        isSelected ? "bg-amber-50/80" : "hover:bg-slate-50"
                      }`}
                    >
                      <span
                        className={`grid h-8 w-8 shrink-0 place-items-center rounded-xl ${
                          isSelected ? "bg-amber-600 text-white" : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        <MapPin size={16} />
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <p className="truncate text-sm font-semibold text-slate-900">{loc.title}</p>
                          <span className="shrink-0 rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-600">
                            {loc.zone}
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-slate-500">
                          <p className="truncate">{loc.subtitle}</p>
                          <span className="shrink-0 flex items-center gap-1 text-[11px] font-medium text-emerald-700">
                            <ShieldCheck size={11} /> {loc.spots} spots
                          </span>
                        </div>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          )}
        </div>

        {/* When Section */}
        <div className="mt-5">
          <p className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-600">
            <Clock size={13} className="text-amber-600" /> When
          </p>
          <div className="flex flex-wrap gap-2">
            {TIME_OPTIONS.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setWhen(option)}
                className={`rounded-full border px-4 py-2 text-[13px] font-semibold transition-all duration-150 active:scale-95 ${
                  when === option
                    ? "border-amber-600 bg-amber-600 text-white shadow-sm active:bg-amber-700 font-bold"
                    : "border-slate-300 bg-white text-slate-700 hover:border-amber-400 hover:bg-amber-50/50 active:bg-slate-100 font-medium"
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
              className="mt-3 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-500/20"
            />
          )}
        </div>

        {/* Recent Section */}
        <div className="mt-6">
          <p className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-600">Recent Searches</p>
          <div className="space-y-1">
            {RECENTS.map((place) => (
              <button
                key={place}
                type="button"
                onClick={() => {
                  setDestination(place);
                  handleSearch(place);
                }}
                className="flex w-full items-center gap-3 rounded-xl px-2.5 py-2.5 text-left transition-colors hover:bg-amber-50/60 active:bg-amber-100/50"
              >
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-slate-100 text-slate-600">
                  <MapPin size={15} />
                </span>
                <span className="truncate text-sm font-medium text-slate-800">{place}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <BottomActionBar>
        <Button
          size="lg"
          fullWidth
          disabled={!canSearch}
          onClick={() => handleSearch()}
          className="shadow-md shadow-amber-600/20"
        >
          Find Parking
        </Button>
      </BottomActionBar>
    </Screen>
  );
}
