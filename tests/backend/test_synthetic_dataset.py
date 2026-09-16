"""Unit tests verifying completeness, schema correctness, and scenarios in the synthetic dataset."""

import os
import json
import csv

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic"))

def test_synthetic_files_exist():
    json_path = os.path.join(DATA_DIR, "veripark_smart_parking_dataset.json")
    csv_path = os.path.join(DATA_DIR, "veripark_smart_parking_dataset.csv")
    assert os.path.exists(json_path), f"JSON dataset missing at {json_path}"
    assert os.path.exists(csv_path), f"CSV dataset missing at {csv_path}"

def test_synthetic_json_schema_and_completeness():
    json_path = os.path.join(DATA_DIR, "veripark_smart_parking_dataset.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert "metadata" in data
    assert "lots" in data
    lots = data["lots"]
    assert len(lots) >= 8

    required_fields = [
        "lot_id", "lot_name", "zone", "address", "latitude", "longitude",
        "lot_type", "total_spots", "occupied_spots", "spots_available",
        "occupancy_rate", "base_rate_per_hour", "ev_charging_spots",
        "handicap_spots", "amenities", "rating", "live_signals", "vericore_scenario"
    ]

    for lot in lots:
        for field in required_fields:
            assert field in lot, f"Field '{field}' missing from lot {lot.get('lot_id')}"
        
        assert lot["total_spots"] > 0
        assert 0 <= lot["occupancy_rate"] <= 1.0
        assert lot["base_rate_per_hour"] > 0
        assert len(lot["amenities"]) > 0
        
        signals = lot["live_signals"]
        assert "camera_feed_active" in signals
        assert "weather" in signals
        assert "traffic_density" in signals

def test_synthetic_csv_completeness_and_columns():
    csv_path = os.path.join(DATA_DIR, "veripark_smart_parking_dataset.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) >= 8
    expected_cols = [
        "lot_id", "lot_name", "zone", "address", "latitude", "longitude",
        "lot_type", "total_spots", "occupied_spots", "spots_available",
        "occupancy_rate_pct", "base_rate_per_hour_inr", "ev_charging_spots",
        "handicap_spots", "rating", "amenities_list", "weather_condition",
        "traffic_density", "nearby_event_name", "camera_feed_active",
        "unverified_surcharge_detected", "vericore_scenario_name"
    ]
    for col in expected_cols:
        assert col in reader.fieldnames, f"Column '{col}' missing from CSV"

def test_vericore_test_scenarios_represented():
    json_path = os.path.join(DATA_DIR, "veripark_smart_parking_dataset.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    scenarios = [l["vericore_scenario"]["scenario_name"] for l in data["lots"]]
    assert any("Hallucination" in s or "Street Fair" in s for s in scenarios)
    assert any("Clean" in s or "Entailment" in s for s in scenarios)
    assert any("Live Re-Grounding" in s or "Event" in s for s in scenarios)
    assert any("Policy" in s or "Healthcare" in s for s in scenarios)
