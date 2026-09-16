"""End-to-End System Integration Test for VeriPark & VeriCore™ Assurance Engine."""

import pytest
from fastapi.testclient import TestClient
from veripark.api.main import app

client = TestClient(app)

def test_full_driver_and_operator_flow():
    # 1. Driver performs search
    search_res = client.post("/api/search", json={"destination": "Brigade Road / MG Road", "duration_hours": 2})
    assert search_res.status_code == 200
    spots = search_res.json()
    assert len(spots) >= 3

    # Pick the metro hub lot which has the unverified street fair factor
    metro_spot = next((s for s in spots if "lot-metro-hub" in s["lot_id"]), spots[0])
    dec_id = metro_spot["decision_id"]

    # 2. Driver inspects Decision Detail
    detail_res = client.get(f"/api/decisions/{dec_id}")
    assert detail_res.status_code == 200
    decision = detail_res.json()

    # In lot-metro-hub, an unverified street fair factor was caught and clamped
    assert decision["was_adjusted"] is True
    assert decision["final_price"] < decision["proposed_price"]
    assert decision["delta"] > 0
    assert "clamped" in decision["adjustment_reason"].lower() or "adjusted" in decision["adjustment_reason"].lower()

    # 3. Driver opens Verification Detail
    v_res = client.get(f"/api/decisions/{dec_id}/verification")
    assert v_res.status_code == 200
    factors = v_res.json()
    assert len(factors) >= 3

    # Verify friendly labels are strictly enforced
    for f in factors:
        assert f["check_label"] in ["Quick check", "Careful check", "Rechecked live just now"]
        assert f["verdict"] in ["Verified", "Excluded — couldn't be verified", "Verified against live data"]

    # Check that at least one factor was excluded and removed from price
    excluded_factors = [f for f in factors if "Excluded" in f["verdict"]]
    assert len(excluded_factors) >= 1

    # 4. Driver opens Cryptographic Audit Trail
    ledger_res = client.get(f"/api/decisions/{dec_id}/ledger")
    assert ledger_res.status_code == 200
    ledger_entry = ledger_res.json()
    assert len(ledger_entry["block_hash"]) == 64
    assert len(ledger_entry["evidence_hash"]) == 64
    assert ledger_entry["sealed"] is True

    # 5. Driver clicks 'Verify record integrity'
    verify_res = client.post(f"/api/decisions/{dec_id}/verify-record")
    assert verify_res.status_code == 200
    verification_check = verify_res.json()
    assert verification_check["valid"] is True
    assert verification_check["chain_valid"] is True

    # 6. Driver Confirms & Books the spot
    booking_res = client.post("/api/bookings", json={
        "decision_id": dec_id,
        "contact_info": {
            "name": "Arjun Rao",
            "phone": "+91 98450 12345"
        },
        "vehicle_plate": "KA 05 MN 4321"
    })
    assert booking_res.status_code == 200
    booking = booking_res.json()
    assert booking["status"] == "confirmed"
    assert booking["booking_id"].startswith("BK-")
    assert booking["final_price"] == decision["final_price"]

    # 7. Operator reviews Dashboard Stats
    stats_res = client.get("/api/admin/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_decisions"] > 0
    assert stats["adjustment_rate"] > 0
    assert stats["verification_cost_reduction_pct"] > 40.0
    assert len(stats["trend"]) >= 5
