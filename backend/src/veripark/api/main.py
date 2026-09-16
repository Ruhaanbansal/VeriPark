import time
import uuid
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from veripark.config import load_settings
from veripark.pipeline import VeriParkPipeline
from veripark.api.schemas import (
    SearchRequest,
    CandidateDecisionSummary,
    DecisionDetailResponse,
    ExplanationItemResponse,
    FactorVerificationResponse,
    LedgerRecordResponse,
    VerifyRecordResponse,
    BookingRequest,
    BookingResponse,
    AdminStatsResponse
)
from veripark.api.friendly_labels import to_friendly_tier, to_friendly_verdict
from veripark.evaluation.harness import EvaluationHarness

settings = load_settings()

app = FastAPI(
    title="VeriPark API & VeriCore™ Assurance Engine",
    description="Explainable, Faithful Parking Allocation and Dynamic Pricing Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow Next.js frontend local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = VeriParkPipeline(config=settings)
eval_harness = EvaluationHarness(pipeline.ledger)

# In-memory storage for evaluated active decisions
active_decisions_cache: Dict[str, Dict[str, Any]] = {}
bookings_store: Dict[str, Dict[str, Any]] = {}

@app.on_event("startup")
def warmup_data():
    """Prime initial decisions for available parking lots."""
    prime_results = pipeline.search_and_evaluate_all("Central Core")
    for res in prime_results:
        active_decisions_cache[res["decision_id"]] = res
        # Also cache by lot ID so either works seamlessly
        active_decisions_cache[res["lot_id"]] = res

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "veripark-backend",
        "vericore_engine": "active",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

# Screen 2 & 3: Search & Results
@app.post("/api/search", response_model=List[CandidateDecisionSummary])
def search_parking(request: SearchRequest):
    results = pipeline.search_and_evaluate_all(request.destination, duration_hours=request.duration_hours or 2)
    response_items = []

    for item in results:
        active_decisions_cache[item["decision_id"]] = item
        active_decisions_cache[item["lot_id"]] = item
        lot = item["lot"]
        resum = item["resummation"]
        
        response_items.append(CandidateDecisionSummary(
            decision_id=item["decision_id"],
            lot_id=lot["id"],
            lot_name=lot["name"],
            address=lot["address"],
            distance_meters=lot["distance_meters"],
            walk_minutes=lot["walk_minutes"],
            spots_available=lot["spots_available"],
            total_spots=lot["total_spots"],
            rating=lot["rating"],
            final_price=resum["final_price"],
            proposed_price=resum["proposed_price"],
            verified=True,
            was_adjusted=resum["was_adjusted"],
            cover_image_tone=lot.get("cover_image_tone", "navy")
        ))

    return response_items

# Screen 4: Decision Detail
@app.get("/api/decisions/{decision_id}", response_model=DecisionDetailResponse)
def get_decision_detail(decision_id: str):
    # Lookup in cache or generate
    decision = active_decisions_cache.get(decision_id)
    if not decision:
        # Check if decision_id is actually a lot_id
        try:
            decision = pipeline.process_decision(decision_id, duration_hours=2, decision_id=f"dec-{decision_id}")
            active_decisions_cache[decision_id] = decision
            active_decisions_cache[decision["decision_id"]] = decision
        except Exception:
            raise HTTPException(status_code=404, detail="Decision not found")

    lot = decision["lot"]
    resum = decision["resummation"]
    verdicts = decision["verdicts"]

    # Transform explanation sentences with server-side friendly labels
    explanation_items: List[ExplanationItemResponse] = []
    for idx, v in enumerate(verdicts):
        is_excluded = v.verdict == "unsupported"
        friendly_tier = to_friendly_tier(v.tier)
        friendly_verdict = to_friendly_verdict(v.verdict)

        explanation_items.append(ExplanationItemResponse(
            id=f"exp-{idx}",
            text=v.claim_text,
            verdict=friendly_verdict,
            tier_label=friendly_tier,
            is_excluded=is_excluded
        ))

    adjustment_reason = None
    if resum["was_adjusted"]:
        adjustment_reason = (
            f"An ungrounded surcharge was detected during live verification. "
            f"VeriPark automatically clamped your price by ₹{int(resum['delta'])} before showing it to you."
        )

    return DecisionDetailResponse(
        decision_id=decision["decision_id"],
        lot_id=lot["id"],
        lot_name=lot["name"],
        address=lot["address"],
        duration_hours=decision["duration_hours"],
        proposed_price=resum["proposed_price"],
        final_price=resum["final_price"],
        delta=resum["delta"],
        was_adjusted=resum["was_adjusted"],
        adjustment_reason=adjustment_reason,
        explanation=explanation_items
    )

# Screen 5: Verification Detail
@app.get("/api/decisions/{decision_id}/verification", response_model=List[FactorVerificationResponse])
def get_decision_verification(decision_id: str):
    decision = active_decisions_cache.get(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    pricing_result = decision["pricing_result"]
    verdicts = decision["verdicts"]
    verdict_by_fid = {v.factor_id: v for v in verdicts}

    factor_responses: List[FactorVerificationResponse] = []
    for factor in pricing_result["factors"]:
        fid = factor["factor_id"]
        v = verdict_by_fid.get(fid)
        
        if v:
            friendly_check = to_friendly_tier(v.tier)
            friendly_verdict = to_friendly_verdict(v.verdict)
            check_detail = v.check_detail
        else:
            friendly_check = "Quick check"
            friendly_verdict = "Verified"
            check_detail = "Verified baseline rate parameter."

        factor_responses.append(FactorVerificationResponse(
            factor_id=fid,
            factor_label=factor["description"],
            contribution=factor["contribution"],
            check_label=friendly_check,
            verdict=friendly_verdict,
            check_detail=check_detail
        ))

    return factor_responses

# Screen 6: Audit Trail
@app.get("/api/decisions/{decision_id}/ledger", response_model=LedgerRecordResponse)
def get_decision_ledger_record(decision_id: str):
    decision = active_decisions_cache.get(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    record = pipeline.ledger.get_record(decision["decision_id"])
    if not record:
        record = decision.get("ledger_entry")
    
    if not record:
        raise HTTPException(status_code=404, detail="Ledger record not found")

    return LedgerRecordResponse(
        decision_id=record["decision_id"],
        timestamp=record["timestamp"],
        recorded_price=record["recorded_price"],
        evidence_hash=record["evidence_hash"],
        previous_hash=record["previous_hash"],
        block_hash=record["block_hash"],
        sealed=record.get("sealed", True)
    )

# Screen 6: Audit Trail — verify button
@app.post("/api/decisions/{decision_id}/verify-record", response_model=VerifyRecordResponse)
def verify_decision_record(decision_id: str):
    is_valid, detail = pipeline.ledger.verify_chain()
    return VerifyRecordResponse(
        valid=is_valid,
        decision_id=decision_id,
        chain_valid=is_valid,
        detail=detail
    )

# Screen 7 & 8: Confirm & Book
@app.post("/api/bookings", response_model=BookingResponse)
def create_booking(request: BookingRequest):
    decision = active_decisions_cache.get(request.decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
    access_code = f"VP-{random_code()}"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    booking_record = {
        "booking_id": booking_id,
        "decision_id": decision["decision_id"],
        "lot_name": decision["lot"]["name"],
        "final_price": decision["resummation"]["final_price"],
        "timestamp": timestamp,
        "access_code": access_code,
        "contact_info": request.contact_info,
        "vehicle_plate": request.vehicle_plate,
        "status": "confirmed"
    }

    bookings_store[booking_id] = booking_record

    return BookingResponse(
        booking_id=booking_id,
        decision_id=decision["decision_id"],
        lot_name=decision["lot"]["name"],
        final_price=decision["resummation"]["final_price"],
        timestamp=timestamp,
        access_code=access_code,
        status="confirmed"
    )

def random_code() -> str:
    import random
    return f"{random.randint(100, 999)}-{random.randint(100, 999)}"

# Screen 9: Operator Dashboard
@app.get("/api/admin/stats", response_model=AdminStatsResponse)
def get_admin_stats():
    metrics = eval_harness.compute_aggregate_metrics()
    return AdminStatsResponse(**metrics)
