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
    id: "lot-mg-road",
    name: "MG Road Central Parkade",
    address: "MG Road, near Trinity Circle",
    distanceMeters: 240,
    walkMinutes: 3,
    spotsAvailable: 14,
    totalSpots: 120,
    rating: 4.6,
    finalPrice: 65,
    wasAdjusted: true,
    status: "adjusted",
    coverImageTone: "navy",
  },
  {
    id: "lot-brigade",
    name: "Brigade Towers Basement",
    address: "Brigade Road, Gate 2",
    distanceMeters: 420,
    walkMinutes: 5,
    spotsAvailable: 31,
    totalSpots: 200,
    rating: 4.4,
    finalPrice: 45,
    wasAdjusted: false,
    status: "verified",
    coverImageTone: "teal",
  },
  {
    id: "lot-indiranagar",
    name: "Indiranagar Metro Lot",
    address: "100 Ft Road, near Metro Exit 2",
    distanceMeters: 610,
    walkMinutes: 8,
    spotsAvailable: 6,
    totalSpots: 80,
    rating: 4.2,
    finalPrice: 80,
    wasAdjusted: true,
    status: "adjusted",
    coverImageTone: "amber",
  },
  {
    id: "lot-cubbon",
    name: "Cubbon Park Roadside Lot",
    address: "Kasturba Road, opposite High Court",
    distanceMeters: 780,
    walkMinutes: 10,
    spotsAvailable: 22,
    totalSpots: 60,
    rating: 4.0,
    finalPrice: 35,
    wasAdjusted: false,
    status: "verified",
    coverImageTone: "teal",
  },
];

const DECISIONS: Record<string, Decision> = {
  "lot-mg-road": {
    id: "VP-2026-04213",
    lot: LOTS[0],
    timestamp: "2026-02-14T18:42:00+05:30",
    durationHours: 3,
    originalPrice: 80,
    finalPrice: 65,
    wasAdjusted: true,
    adjustmentAmount: 15,
    adjustmentReason:
      "Lowered by ₹15 — the claimed concert nearby couldn't be confirmed against the venue's live schedule.",
    explanation: [
      {
        id: "s1",
        text: "This spot is priced from a base rate of ₹40 for the MG Road zone.",
        status: "verified",
        factorId: "base",
      },
      {
        id: "s2",
        text: "Occupancy nearby is high right now (91% full), which adds ₹20.",
        status: "checked_live",
        factorId: "occupancy",
      },
      {
        id: "s3",
        text: "A nearby concert was initially expected to add ₹15, but this could not be confirmed against the venue's live schedule, so it has been removed from your price.",
        status: "excluded",
        factorId: "event",
      },
      {
        id: "s4",
        text: "Light evening rain is increasing demand for covered parking, adding ₹5.",
        status: "verified",
        factorId: "weather",
      },
    ],
    factors: [
      {
        id: "base",
        label: "Base rate",
        description: "The standard listed rate for this zone at this time of day.",
        amount: 40,
        tier: "quick",
        checkDetail: "Matched directly against the operator's published rate card.",
        status: "verified",
      },
      {
        id: "occupancy",
        label: "Nearby occupancy",
        description: "How full nearby lots are right now, which affects demand-based pricing.",
        amount: 20,
        tier: "careful",
        checkDetail: "Cross-checked against two independent camera feeds reporting 91% and 89% full.",
        status: "verified",
      },
      {
        id: "event",
        label: "Nearby event",
        description: "A large nearby event that was expected to increase demand.",
        amount: 0,
        tier: "live",
        checkDetail:
          "Rechecked live against the venue's official schedule just now — no event was found at the claimed time, so this amount was removed.",
        status: "excluded",
      },
      {
        id: "weather",
        label: "Weather",
        description: "Current weather conditions that change how many drivers want covered parking.",
        amount: 5,
        tier: "quick",
        checkDetail: "Matched against a live regional weather feed updated 4 minutes ago.",
        status: "verified",
      },
    ],
    ledger: {
      decisionId: "VP-2026-04213",
      timestamp: "2026-02-14T18:42:03+05:30",
      recordedPrice: 65,
      evidenceHash: hash("evidence-VP-2026-04213"),
      previousHash: hash("prev-VP-2026-04212"),
      blockHash: hash("block-VP-2026-04213"),
      sealed: true,
    },
    verificationSummary: {
      totalClaims: 4,
      verifiedClaims: 2,
      liveRecheckedClaims: 1,
      excludedClaims: 1,
    },
  },
  "lot-brigade": {
    id: "VP-2026-04214",
    lot: LOTS[1],
    timestamp: "2026-02-14T18:44:10+05:30",
    durationHours: 3,
    originalPrice: 45,
    finalPrice: 45,
    wasAdjusted: false,
    adjustmentAmount: 0,
    adjustmentReason: "",
    explanation: [
      {
        id: "s1",
        text: "This spot is priced from a base rate of ₹35 for the Brigade Road zone.",
        status: "verified",
        factorId: "base",
      },
      {
        id: "s2",
        text: "Occupancy nearby is moderate (62% full), adding ₹10.",
        status: "verified",
        factorId: "occupancy",
      },
    ],
    factors: [
      {
        id: "base",
        label: "Base rate",
        description: "The standard listed rate for this zone at this time of day.",
        amount: 35,
        tier: "quick",
        checkDetail: "Matched directly against the operator's published rate card.",
        status: "verified",
      },
      {
        id: "occupancy",
        label: "Nearby occupancy",
        description: "How full nearby lots are right now, which affects demand-based pricing.",
        amount: 10,
        tier: "quick",
        checkDetail: "Matched against a live camera feed reporting 62% full.",
        status: "verified",
      },
    ],
    ledger: {
      decisionId: "VP-2026-04214",
      timestamp: "2026-02-14T18:44:13+05:30",
      recordedPrice: 45,
      evidenceHash: hash("evidence-VP-2026-04214"),
      previousHash: hash("prev-VP-2026-04213"),
      blockHash: hash("block-VP-2026-04214"),
      sealed: true,
    },
    verificationSummary: {
      totalClaims: 2,
      verifiedClaims: 2,
      liveRecheckedClaims: 0,
      excludedClaims: 0,
    },
  },
  "lot-indiranagar": {
    id: "VP-2026-04215",
    lot: LOTS[2],
    timestamp: "2026-02-14T18:46:00+05:30",
    durationHours: 2,
    originalPrice: 95,
    finalPrice: 80,
    wasAdjusted: true,
    adjustmentAmount: 15,
    adjustmentReason:
      "Lowered by ₹15 — a claimed traffic diversion nearby did not match the live traffic feed.",
    explanation: [
      {
        id: "s1",
        text: "This spot is priced from a base rate of ₹45 for the Indiranagar metro zone.",
        status: "verified",
        factorId: "base",
      },
      {
        id: "s2",
        text: "Very few spots remain nearby (6 of 80), which adds ₹35.",
        status: "checked_live",
        factorId: "occupancy",
      },
      {
        id: "s3",
        text: "A claimed traffic diversion was expected to add ₹15, but this did not match the live traffic feed, so it has been removed from your price.",
        status: "excluded",
        factorId: "traffic",
      },
    ],
    factors: [
      {
        id: "base",
        label: "Base rate",
        description: "The standard listed rate for this zone at this time of day.",
        amount: 45,
        tier: "quick",
        checkDetail: "Matched directly against the operator's published rate card.",
        status: "verified",
      },
      {
        id: "occupancy",
        label: "Nearby occupancy",
        description: "How full nearby lots are right now, which affects demand-based pricing.",
        amount: 35,
        tier: "live",
        checkDetail: "Rechecked live against the metro lot's camera feed just now — confirms 6 of 80 spots free.",
        status: "checked_live",
      },
      {
        id: "traffic",
        label: "Traffic diversion",
        description: "A nearby road diversion that was expected to increase demand for this lot.",
        amount: 0,
        tier: "live",
        checkDetail:
          "Rechecked live against the city traffic authority feed just now — no active diversion found, so this amount was removed.",
        status: "excluded",
      },
    ],
    ledger: {
      decisionId: "VP-2026-04215",
      timestamp: "2026-02-14T18:46:04+05:30",
      recordedPrice: 80,
      evidenceHash: hash("evidence-VP-2026-04215"),
      previousHash: hash("prev-VP-2026-04214"),
      blockHash: hash("block-VP-2026-04215"),
      sealed: true,
    },
    verificationSummary: {
      totalClaims: 3,
      verifiedClaims: 1,
      liveRecheckedClaims: 1,
      excludedClaims: 1,
    },
  },
  "lot-cubbon": {
    id: "VP-2026-04216",
    lot: LOTS[3],
    timestamp: "2026-02-14T18:47:20+05:30",
    durationHours: 4,
    originalPrice: 35,
    finalPrice: 35,
    wasAdjusted: false,
    adjustmentAmount: 0,
    adjustmentReason: "",
    explanation: [
      {
        id: "s1",
        text: "This spot is priced from a flat base rate of ₹30 for roadside zones.",
        status: "verified",
        factorId: "base",
      },
      {
        id: "s2",
        text: "Occupancy nearby is low (37% full), adding ₹5.",
        status: "verified",
        factorId: "occupancy",
      },
    ],
    factors: [
      {
        id: "base",
        label: "Base rate",
        description: "The standard flat rate for roadside parking zones.",
        amount: 30,
        tier: "quick",
        checkDetail: "Matched directly against the operator's published rate card.",
        status: "verified",
      },
      {
        id: "occupancy",
        label: "Nearby occupancy",
        description: "How full nearby lots are right now, which affects demand-based pricing.",
        amount: 5,
        tier: "quick",
        checkDetail: "Matched against a live camera feed reporting 37% full.",
        status: "verified",
      },
    ],
    ledger: {
      decisionId: "VP-2026-04216",
      timestamp: "2026-02-14T18:47:23+05:30",
      recordedPrice: 35,
      evidenceHash: hash("evidence-VP-2026-04216"),
      previousHash: hash("prev-VP-2026-04215"),
      blockHash: hash("block-VP-2026-04216"),
      sealed: true,
    },
    verificationSummary: {
      totalClaims: 2,
      verifiedClaims: 2,
      liveRecheckedClaims: 0,
      excludedClaims: 0,
    },
  },
};

export function getLots(): ParkingLot[] {
  return LOTS;
}

export function getLotById(id: string): ParkingLot | undefined {
  return LOTS.find((l) => l.id === id);
}

export function getDecisionByLotId(id: string): Decision | undefined {
  return DECISIONS[id];
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
