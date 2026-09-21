from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ==========================================
# Agent / Internal Data Contracts
# ==========================================

class PricingFactor(BaseModel):
    factor_id: str
    description: str
    contribution: float

class PricingResult(BaseModel):
    recommended_lot_id: str
    base_price: float
    factors: List[PricingFactor]
    proposed_price: float

class DraftClaim(BaseModel):
    claim_text: str
    factor_id: str

class ClaimVerdict(BaseModel):
    claim_text: str
    factor_id: str
    materiality: float
    tier: str  # internal enum: "light" | "standard" | "deep"
    verdict: str  # internal enum: "supported" | "unsupported" | "live_reverified"
    check_detail: str

class ResummationResult(BaseModel):
    final_price: float
    proposed_price: float
    delta: float
    excluded_factors: List[str]
    was_adjusted: bool

# ==========================================
# Client-Facing API Schemas (Friendly Labels)
# ==========================================

class SearchRequest(BaseModel):
    destination: str
    datetime: Optional[str] = None
    duration_hours: Optional[int] = 2

class CandidateDecisionSummary(BaseModel):
    decision_id: str
    lot_id: str
    lot_name: str
    address: str
    distance_meters: int
    walk_minutes: int
    spots_available: int
    total_spots: int
    rating: float
    final_price: float
    proposed_price: float
    verified: bool
    was_adjusted: bool
    cover_image_tone: str = "navy"

class ExplanationItemResponse(BaseModel):
    id: str
    text: str
    verdict: str  # e.g. "Verified", "Excluded — couldn't be verified", "Verified against live data"
    tier_label: str  # e.g. "Quick check", "Careful check", "Rechecked live just now"
    is_excluded: bool = False

class DecisionDetailResponse(BaseModel):
    decision_id: str
    lot_id: str
    lot_name: str
    address: str
    duration_hours: int
    proposed_price: float
    final_price: float
    delta: float
    was_adjusted: bool
    adjustment_reason: Optional[str] = None
    explanation: List[ExplanationItemResponse]
    # Lot metadata (carried through for frontend display)
    distance_meters: int = 300
    walk_minutes: int = 4
    spots_available: int = 0
    total_spots: int = 0
    rating: float = 4.5
    cover_image_tone: str = "amber"
    amenities: List[str] = Field(default_factory=list)
    lot_type: str = "underground_multi_level"
    base_price: float = 0.0

class FactorVerificationResponse(BaseModel):
    factor_id: str
    factor_label: str
    contribution: float
    check_label: str  # Friendly tier name, e.g. "Rechecked live just now"
    verdict: str  # Friendly verdict name, e.g. "Verified"
    check_detail: str

class LedgerRecordResponse(BaseModel):
    decision_id: str
    timestamp: str
    recorded_price: float
    evidence_hash: str
    previous_hash: str
    block_hash: str
    sealed: bool

class VerifyRecordResponse(BaseModel):
    valid: bool
    decision_id: str
    chain_valid: bool
    detail: str

class BookingRequest(BaseModel):
    decision_id: str
    contact_info: Dict[str, Any]
    vehicle_plate: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    decision_id: str
    lot_name: str
    final_price: float
    timestamp: str
    access_code: str
    status: str = "confirmed"

class TrendPoint(BaseModel):
    date: str
    count: int
    adjustment_rate: float

class AdminStatsResponse(BaseModel):
    total_decisions: int
    adjustment_rate: float
    avg_adjustment_amount: float
    verification_cost_reduction_pct: float
    trend: List[TrendPoint]
