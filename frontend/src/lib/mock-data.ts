import type { Decision, OperatorTrendPoint, ParkingLot } from "./types";

// ---------------------------------------------------------------------------
// This module simulates the responses that will eventually come from
// VeriPark's backend (Context Retrieval → Pricing → Explanation → VeriCore →
// Ledger). Every function here is written so a future swap to `fetch("/api/...")`
// requires no change to the calling components.
// ---------------------------------------------------------------------------

function hash(seed: string): string {
  let h1 = 0xdeadbeef ^ seed.length;
  let h2 = 0x41c6ce57 ^ seed.length;
  for (let i = 0; i < seed.length; i++) {
    const ch = seed.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = (h1 ^ (h1 >>> 16)) >>> 0;
  h2 = (h2 ^ (h2 >>> 16)) >>> 0;
  return (h1.toString(16).padStart(8, "0") + h2.toString(16).padStart(8, "0")).repeat(2).slice(0, 64);
}

const LOTS: ParkingLot[] = [
  {
    id: "lot-metro-hub",
    decisionId: "dec-lot-metro-hub",
    name: "MG Road Metro Transit Hub Deck",
    address: "Brigade Rd / MG Rd Junction",
    distanceMeters: 180,
    walkMinutes: 2,
    spotsAvailable: 14,
    totalSpots: 120,
    rating: 4.8,
    finalPrice: 65,
    originalPrice: 95,
    wasAdjusted: true,
    status: "adjusted",
    coverImageTone: "amber",
    coverAsset: "/images/lots/lot-metro-hub.jpg",
  },
  {
    id: "lot-commercial-tower",
    decisionId: "dec-lot-commercial-tower",
    name: "Prestige Commercial Plaza Deck",
    address: "Residency Road, Commercial Zone",
    distanceMeters: 420,
    walkMinutes: 5,
    spotsAvailable: 46,
    totalSpots: 250,
    rating: 4.6,
    finalPrice: 45,
    originalPrice: 45,
    wasAdjusted: false,
    status: "verified",
    coverImageTone: "teal",
    coverAsset: "/images/lots/lot-commercial-tower.jpg",
  },
  {
    id: "lot-civic-center",
    decisionId: "dec-lot-civic-center",
    name: "Town Hall Civic Underground",
    address: "JC Road, Civic Center",
    distanceMeters: 750,
    walkMinutes: 9,
    spotsAvailable: 72,
    totalSpots: 180,
    rating: 4.3,
    finalPrice: 35,
    originalPrice: 35,
    wasAdjusted: false,
    status: "verified",
    coverImageTone: "amber",
    coverAsset: "/images/lots/lot-civic-center.jpg",
  },
  {
    id: "lot-indiranagar-100ft",
    decisionId: "dec-lot-indiranagar-100ft",
    name: "Indiranagar 100ft Smart Vault",
    address: "100 Feet Road, Near HAL 2nd Stage",
    distanceMeters: 220,
    walkMinutes: 3,
    spotsAvailable: 14,
    totalSpots: 160,
    rating: 4.9,
    finalPrice: 70,
    originalPrice: 90,
    wasAdjusted: true,
    status: "adjusted",
    coverImageTone: "amber",
    coverAsset: "/images/lots/lot-indiranagar.jpg",
  },
  {
    id: "lot-hospital-emergency",
    decisionId: "dec-lot-hospital-emergency",
    name: "Manipal Hospital Emergency & OPD Deck",
    address: "Old Airport Road, Kodihalli",
    distanceMeters: 110,
    walkMinutes: 1,
    spotsAvailable: 18,
    totalSpots: 140,
    rating: 4.8,
    finalPrice: 40,
    originalPrice: 65,
    wasAdjusted: true,
    status: "adjusted",
    coverImageTone: "amber",
    coverAsset: "/images/lots/lot-hospital.jpg",
  },
  {
    id: "lot-koramangala-nexus",
    decisionId: "dec-lot-koramangala-nexus",
    name: "Koramangala Nexus Transit Plaza",
    address: "80 Feet Road, 4th Block Koramangala",
    distanceMeters: 310,
    walkMinutes: 4,
    spotsAvailable: 110,
    totalSpots: 320,
    rating: 4.7,
    finalPrice: 50,
    originalPrice: 50,
    wasAdjusted: false,
    status: "verified",
    coverImageTone: "teal",
    coverAsset: "/images/lots/lot-koramangala.jpg",
  },
  {
    id: "lot-express-deck",
    decisionId: "dec-lot-express-deck",
    name: "Richmond Circle Automated Deck",
    address: "Richmond Rd, Flyover Entrance",
    distanceMeters: 950,
    walkMinutes: 12,
    spotsAvailable: 28,
    totalSpots: 80,
    rating: 4.5,
    finalPrice: 55,
    originalPrice: 55,
    wasAdjusted: false,
    status: "verified",
    coverImageTone: "teal",
    coverAsset: "/images/lots/lot-express-deck.jpg",
  },
];

// ---- Decision data keyed by BOTH lot ID and decision ID for stable lookup ----

function makeDecision(
  decisionId: string,
  lot: ParkingLot,
  timestamp: string,
  durationHours: number,
  originalPrice: number,
  finalPrice: number,
  wasAdjusted: boolean,
  adjustmentAmount: number,
  adjustmentReason: string,
  explanation: Decision["explanation"],
  factors: Decision["factors"],
  verificationSummary: Decision["verificationSummary"]
): Decision {
  return {
    id: decisionId,
    lot: { ...lot, decisionId },
    timestamp,
    durationHours,
    originalPrice,
    finalPrice,
    wasAdjusted,
    adjustmentAmount,
    adjustmentReason,
    explanation,
    factors,
    ledger: {
      decisionId,
      timestamp,
      recordedPrice: finalPrice,
      evidenceHash: hash(`evidence-${decisionId}`),
      previousHash: hash(`prev-${decisionId}`),
      blockHash: hash(`block-${decisionId}`),
      sealed: true,
    },
    verificationSummary,
  };
}

const DEC_METRO = makeDecision(
  "dec-lot-metro-hub",
  LOTS[0],
  "2026-09-16T18:42:00+05:30",
  3,
  95,
  65,
  true,
  30,
  "Lowered by ₹30 — an unverified street-fair exclusion zone surcharge was automatically removed by VeriCore™.",
  [
    { id: "s1", text: "Base rate of ₹30 for the MG Road zone.", status: "verified", factorId: "base" },
    { id: "s2", text: "Occupancy is surging past 85% — only 14 spots left — adding ₹35.", status: "checked_live", factorId: "occupancy" },
    { id: "s3", text: "A street-fair exclusion zone surcharge of ₹30 was proposed but couldn't be verified against any city traffic source, so it has been removed from your price.", status: "excluded", factorId: "festival-surcharge" },
  ],
  [
    { id: "base", label: "Base rate", description: "Standard rate for the MG Road zone.", amount: 30, tier: "quick", checkDetail: "Matched against the operator's published rate card.", status: "verified" },
    { id: "occupancy", label: "High occupancy", description: "Only 14 of 120 spots remain — peak demand.", amount: 35, tier: "live", checkDetail: "Rechecked live against gate camera: 14 spots free, 88.3% full. Confirmed.", status: "checked_live" },
    { id: "festival-surcharge", label: "Street-fair surcharge", description: "A claimed city street-fair exclusion zone surcharge.", amount: 0, tier: "live", checkDetail: "Rechecked live — no street-fair or road closure found in the city traffic authority feed. Surcharge removed.", status: "excluded" },
  ],
  { totalClaims: 3, verifiedClaims: 2, liveRecheckedClaims: 1, excludedClaims: 1 }
);

const DEC_COMMERCIAL = makeDecision(
  "dec-lot-commercial-tower",
  LOTS[1],
  "2026-09-16T18:44:10+05:30",
  2,
  45,
  45,
  false,
  0,
  "",
  [
    { id: "s1", text: "Base rate of ₹35 for the Residency Road commercial zone.", status: "verified", factorId: "base" },
    { id: "s2", text: "Moderate occupancy nearby (62% full) adds ₹10.", status: "verified", factorId: "occupancy" },
  ],
  [
    { id: "base", label: "Base rate", description: "Standard rate for the commercial zone.", amount: 35, tier: "quick", checkDetail: "Matched directly against the operator's published rate card.", status: "verified" },
    { id: "occupancy", label: "Nearby occupancy", description: "How full nearby lots are right now.", amount: 10, tier: "quick", checkDetail: "Matched against a live camera feed reporting 62% full.", status: "verified" },
  ],
  { totalClaims: 2, verifiedClaims: 2, liveRecheckedClaims: 0, excludedClaims: 0 }
);

const DEC_CIVIC = makeDecision(
  "dec-lot-civic-center",
  LOTS[2],
  "2026-09-16T18:45:00+05:30",
  2,
  35,
  35,
  false,
  0,
  "",
  [
    { id: "s1", text: "Flat base rate of ₹30 for civic underground zones.", status: "verified", factorId: "base" },
    { id: "s2", text: "Low occupancy (37% full) adds a minimal ₹5.", status: "verified", factorId: "occupancy" },
  ],
  [
    { id: "base", label: "Base rate", description: "Flat rate for civic underground zones.", amount: 30, tier: "quick", checkDetail: "Matched against the operator's published rate card.", status: "verified" },
    { id: "occupancy", label: "Nearby occupancy", description: "How full nearby lots are right now.", amount: 5, tier: "quick", checkDetail: "Matched against a live camera feed reporting 37% full.", status: "verified" },
  ],
  { totalClaims: 2, verifiedClaims: 2, liveRecheckedClaims: 0, excludedClaims: 0 }
);

const DEC_INDIRANAGAR = makeDecision(
  "dec-lot-indiranagar-100ft",
  LOTS[3],
  "2026-09-16T18:46:00+05:30",
  2,
  90,
  70,
  true,
  20,
  "Lowered by ₹20 — a claimed traffic diversion surcharge was removed after live verification found no active diversion.",
  [
    { id: "s1", text: "Base rate of ₹45 for the Indiranagar metro zone.", status: "verified", factorId: "base" },
    { id: "s2", text: "Very few spots remain nearby (14 of 160, just 8.7% free) — adds ₹25.", status: "checked_live", factorId: "occupancy" },
    { id: "s3", text: "A traffic diversion surcharge of ₹20 was expected, but no active diversion was found in the live traffic feed, so it has been removed.", status: "excluded", factorId: "traffic" },
  ],
  [
    { id: "base", label: "Base rate", description: "Standard rate for the Indiranagar zone.", amount: 45, tier: "quick", checkDetail: "Matched against operator rate card.", status: "verified" },
    { id: "occupancy", label: "High occupancy", description: "Critical scarcity — only 14 spots remain.", amount: 25, tier: "live", checkDetail: "Rechecked live against gate sensor: 14 of 160 spots free. Confirmed.", status: "checked_live" },
    { id: "traffic", label: "Traffic diversion", description: "A road diversion expected to increase demand.", amount: 0, tier: "live", checkDetail: "Rechecked live against city traffic authority — no active diversion found. Surcharge removed.", status: "excluded" },
  ],
  { totalClaims: 3, verifiedClaims: 2, liveRecheckedClaims: 1, excludedClaims: 1 }
);

const DEC_HOSPITAL = makeDecision(
  "dec-lot-hospital-emergency",
  LOTS[4],
  "2026-09-16T18:47:00+05:30",
  2,
  65,
  40,
  true,
  25,
  "Lowered by ₹25 — a claimed special emergency-zone surcharge couldn't be confirmed against the hospital operator's live schedule.",
  [
    { id: "s1", text: "Base rate of ₹30 for the hospital emergency deck.", status: "verified", factorId: "base" },
    { id: "s2", text: "High demand for covered spots during the rain adds ₹10.", status: "verified", factorId: "weather" },
    { id: "s3", text: "A special ₹25 emergency-zone surcharge was proposed but could not be confirmed against the hospital's live occupancy data, so it was removed.", status: "excluded", factorId: "ev-premium" },
  ],
  [
    { id: "base", label: "Base rate", description: "Hospital emergency deck base rate.", amount: 30, tier: "quick", checkDetail: "Matched against operator rate card.", status: "verified" },
    { id: "weather", label: "Rain premium", description: "Heavy rain driving demand for covered bays.", amount: 10, tier: "careful", checkDetail: "Cross-checked against two weather feeds — heavy rain confirmed in area.", status: "verified" },
    { id: "ev-premium", label: "Emergency-zone surcharge", description: "A claimed priority emergency zone surcharge.", amount: 0, tier: "live", checkDetail: "Rechecked live — hospital lot registry shows no active emergency overflow condition. Surcharge removed.", status: "excluded" },
  ],
  { totalClaims: 3, verifiedClaims: 2, liveRecheckedClaims: 0, excludedClaims: 1 }
);

const DEC_KORAMANGALA = makeDecision(
  "dec-lot-koramangala-nexus",
  LOTS[5],
  "2026-09-16T18:48:00+05:30",
  2,
  50,
  50,
  false,
  0,
  "",
  [
    { id: "s1", text: "Base rate of ₹40 for the Koramangala transit zone.", status: "verified", factorId: "base" },
    { id: "s2", text: "Moderate occupancy (34% full) adds ₹10.", status: "verified", factorId: "occupancy" },
  ],
  [
    { id: "base", label: "Base rate", description: "Standard rate for the Koramangala zone.", amount: 40, tier: "quick", checkDetail: "Matched against operator rate card.", status: "verified" },
    { id: "occupancy", label: "Nearby occupancy", description: "Moderate demand in the area.", amount: 10, tier: "quick", checkDetail: "Matched against live camera — 34% full.", status: "verified" },
  ],
  { totalClaims: 2, verifiedClaims: 2, liveRecheckedClaims: 0, excludedClaims: 0 }
);

const DEC_EXPRESS = makeDecision(
  "dec-lot-express-deck",
  LOTS[6],
  "2026-09-16T18:49:00+05:30",
  2,
  55,
  55,
  false,
  0,
  "",
  [
    { id: "s1", text: "Base rate of ₹45 for the Richmond Road automated deck.", status: "verified", factorId: "base" },
    { id: "s2", text: "Low occupancy (35% full) adds ₹10.", status: "verified", factorId: "occupancy" },
  ],
  [
    { id: "base", label: "Base rate", description: "Standard rate for the Richmond Road zone.", amount: 45, tier: "quick", checkDetail: "Matched against operator rate card.", status: "verified" },
    { id: "occupancy", label: "Nearby occupancy", description: "Low demand — plenty of spots available.", amount: 10, tier: "quick", checkDetail: "Matched against live camera — 35% full.", status: "verified" },
  ],
  { totalClaims: 2, verifiedClaims: 2, liveRecheckedClaims: 0, excludedClaims: 0 }
);

// Build a lookup map indexed by BOTH lot ID and decision ID
const DECISIONS: Record<string, Decision> = {};
for (const d of [DEC_METRO, DEC_COMMERCIAL, DEC_CIVIC, DEC_INDIRANAGAR, DEC_HOSPITAL, DEC_KORAMANGALA, DEC_EXPRESS]) {
  DECISIONS[d.id] = d;           // e.g. "dec-lot-metro-hub"
  DECISIONS[d.lot.id] = d;       // e.g. "lot-metro-hub"
}

export function getLots(): ParkingLot[] {
  return LOTS;
}

export function getLotById(id: string): ParkingLot | undefined {
  return LOTS.find((l) => l.id === id);
}

/**
 * Returns a decision by EITHER lot ID (lot-metro-hub) or decision ID (dec-lot-metro-hub).
 * Falls back to synthesizing a decision from the first mock decision if no match found.
 */
export function getDecisionByLotId(id: string): Decision | undefined {
  if (DECISIONS[id]) return DECISIONS[id];
  const foundLot = LOTS.find((l) => l.id === id);
  if (foundLot) {
    const baseDec = DEC_METRO;
    return {
      ...baseDec,
      id: `dec-${foundLot.id}`,
      lot: { ...foundLot, decisionId: `dec-${foundLot.id}` },
      finalPrice: foundLot.finalPrice,
      originalPrice: foundLot.originalPrice || foundLot.finalPrice,
      wasAdjusted: foundLot.wasAdjusted,
    };
  }
  return undefined;
}

export const OPERATOR_TREND: OperatorTrendPoint[] = [
  { label: "Mon", decisions: 812, adjustedPct: 6.1 },
  { label: "Tue", decisions: 940, adjustedPct: 7.4 },
  { label: "Wed", decisions: 1024, adjustedPct: 5.8 },
  { label: "Thu", decisions: 1180, adjustedPct: 8.9 },
  { label: "Fri", decisions: 1526, adjustedPct: 11.2 },
  { label: "Sat", decisions: 1890, adjustedPct: 13.6 },
  { label: "Sun", decisions: 1310, adjustedPct: 9.0 },
];

export const OPERATOR_SUMMARY = {
  totalDecisions: 8682,
  adjustedPct: 9.1,
  avgAdjustmentAmount: 14.8,
  verificationCostSavingsPct: 68,
  hallucinationCatchCount: 214,
  avgLatencyMs: 340,
};
