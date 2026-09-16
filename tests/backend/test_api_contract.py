import pytest
import json
from fastapi.testclient import TestClient
from veripark.api.main import app

client = TestClient(app)

FORBIDDEN_RAW_INTERNAL_ENUMS = [
    '"deep"',
    '"unsupported"',
    # Note: "light" and "standard" might appear as substrings in generic English ("standard rate"),
    # but the exact enum values for tier and verdict must never appear as unmapped raw values.
]

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_search_endpoint_contract():
    payload = {"destination": "Central Core", "duration_hours": 2}
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    # Check required fields
    for field in ["decision_id", "lot_id", "lot_name", "final_price", "proposed_price", "verified", "was_adjusted"]:
        assert field in first
    assert first["verified"] is True

def test_decision_detail_contract_and_no_raw_enums():
    # Fetch search first to get valid decision ID
    search_res = client.post("/api/search", json={"destination": "Central Core"})
    dec_id = search_res.json()[0]["decision_id"]

    res = client.get(f"/api/decisions/{dec_id}")
    assert res.status_code == 200
    body_text = res.text

    # Assert NO raw internal enums leaked
    for forbidden in FORBIDDEN_RAW_INTERNAL_ENUMS:
        assert forbidden not in body_text, f"Raw internal enum {forbidden} leaked into API response!"

    data = res.json()
    assert "explanation" in data
    assert len(data["explanation"]) > 0
    for exp in data["explanation"]:
        assert exp["tier_label"] in ["Quick check", "Careful check", "Rechecked live just now", "Checked"]
        assert exp["verdict"] in ["Verified", "Excluded — couldn't be verified", "Verified against live data"]

def test_decision_verification_detail_contract():
    search_res = client.post("/api/search", json={"destination": "Central Core"})
    dec_id = search_res.json()[0]["decision_id"]

    res = client.get(f"/api/decisions/{dec_id}/verification")
    assert res.status_code == 200
    body_text = res.text

    for forbidden in FORBIDDEN_RAW_INTERNAL_ENUMS:
        assert forbidden not in body_text, f"Raw internal enum {forbidden} leaked into verification response!"

    data = res.json()
    assert isinstance(data, list)
    for factor in data:
        assert "factor_id" in factor
        assert "factor_label" in factor
        assert "contribution" in factor
        assert "check_label" in factor
        assert "verdict" in factor

def test_ledger_record_and_verify_endpoints():
    search_res = client.post("/api/search", json={"destination": "Central Core"})
    dec_id = search_res.json()[0]["decision_id"]

    # 1. GET /api/decisions/{id}/ledger
    res_ledger = client.get(f"/api/decisions/{dec_id}/ledger")
    assert res_ledger.status_code == 200
    ledger_data = res_ledger.json()
    assert "block_hash" in ledger_data
    assert "evidence_hash" in ledger_data
    assert "previous_hash" in ledger_data
    assert ledger_data["sealed"] is True

    # 2. POST /api/decisions/{id}/verify-record
    res_verify = client.post(f"/api/decisions/{dec_id}/verify-record")
    assert res_verify.status_code == 200
    verify_data = res_verify.json()
    assert verify_data["valid"] is True
    assert verify_data["chain_valid"] is True

def test_booking_endpoint():
    search_res = client.post("/api/search", json={"destination": "Central Core"})
    dec_id = search_res.json()[0]["decision_id"]

    booking_payload = {
        "decision_id": dec_id,
        "contact_info": {"name": "Priya Sharma", "phone": "+91 98765 43210"},
        "vehicle_plate": "KA 01 AB 1234"
    }
    res = client.post("/api/bookings", json=booking_payload)
    assert res.status_code == 200
    b_data = res.json()
    assert "booking_id" in b_data
    assert "access_code" in b_data
    assert b_data["status"] == "confirmed"

def test_admin_stats_operator_contract():
    res = client.get("/api/admin/stats")
    assert res.status_code == 200
    stats = res.json()
    assert "total_decisions" in stats
    assert "adjustment_rate" in stats
    assert "avg_adjustment_amount" in stats
    assert "verification_cost_reduction_pct" in stats
    assert "trend" in stats
    assert isinstance(stats["trend"], list)
