// Shared domain types for VeriPark.
// These mirror the shape the eventual backend (VeriCore Assurance Engine) will
// return, so the UI can be wired to real API routes later with minimal change.

export type VerificationTier = "quick" | "careful" | "live";

export type ClaimStatus = "verified" | "checked_live" | "excluded";

export interface PriceFactor {
  id: string;
  label: string;
  /** Plain-language description of the factor itself */
  description: string;
  /** Signed rupee contribution to the final price */
  amount: number;
  /** How this factor was checked */
  tier: VerificationTier;
  /** Plain-language detail of what was checked and how */
  checkDetail: string;
  status: ClaimStatus;
}

export interface ExplanationSentence {
  id: string;
  text: string;
  status: ClaimStatus;
  factorId?: string;
}

export interface LedgerRecord {
  decisionId: string;
  timestamp: string;
  recordedPrice: number;
  evidenceHash: string;
  previousHash: string;
  blockHash: string;
  sealed: boolean;
}

export interface ParkingLot {
  id: string;
  name: string;
  address: string;
  distanceMeters: number;
  walkMinutes: number;
  spotsAvailable: number;
  totalSpots: number;
  rating: number;
  finalPrice: number;
  wasAdjusted: boolean;
  status: "verified" | "adjusted";
  coverImageTone: "navy" | "teal" | "amber";
}

export interface Decision {
  id: string;
  lot: ParkingLot;
  timestamp: string;
  durationHours: number;
  originalPrice: number;
  finalPrice: number;
  wasAdjusted: boolean;
  adjustmentAmount: number;
  adjustmentReason: string;
  explanation: ExplanationSentence[];
  factors: PriceFactor[];
  ledger: LedgerRecord;
  verificationSummary: {
    totalClaims: number;
    verifiedClaims: number;
    liveRecheckedClaims: number;
    excludedClaims: number;
  };
}

export interface OperatorTrendPoint {
  label: string;
  decisions: number;
  adjustedPct: number;
}
