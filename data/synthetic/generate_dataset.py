"""Generate professional, complete synthetic smart parking dataset for VeriPark.
Includes comprehensive columns, realistic Bangalore metropolitan locations, live sensors,
and test scenarios covering all VeriCore assurance engine mechanisms.
"""

import json
import csv
import os

SYNTHETIC_LOTS = [
    {
        "lot_id": "lot-metro-hub",
        "lot_name": "MG Road Metro Transit Hub Deck",
        "zone": "Central Core",
        "address": "Brigade Rd / MG Rd Junction, Bangalore 560001",
        "latitude": 12.9756,
        "longitude": 77.6066,
        "lot_type": "underground_multi_level",
        "total_spots": 120,
        "occupied_spots": 106,
        "spots_available": 14,
        "occupancy_rate": 0.883,
        "base_rate_per_hour": 50.0,
        "ev_charging_spots": 12,
        "handicap_spots": 6,
        "operating_hours": "24/7",
        "amenities": ["EV Fast Charging (50kW)", "ANPR FastTag Exit", "CCTV 24/7", "Covered Roof", "Elevator Access"],
        "rating": 4.8,
        "cover_image_tone": "amber",
        "cover_asset": "/images/lots/lot-metro-hub.svg",
        "distance_meters": 180,
        "walk_minutes": 2,
        "live_signals": {
            "occupancy_rate": 0.883,
            "nearby_event": "IPL Screening at Hub Plaza",
            "event_venue": "MG Hub Amphitheater",
            "event_distance_m": 120,
            "event_schedule_verified": True,
            "weather": "Heavy Rain Alert",
            "weather_impact_multiplier": 1.25,
            "traffic_density": "High (Level 4)",
            "traffic_sensor_id": "BLR-TRF-MGR-04",
            "camera_feed_active": True,
            "camera_feed_id": "CAM-MGR-DECK-01",
            "camera_verified_available": 14,
            "sensor_discrepancy_flag": False,
            "unverified_surcharge_flag": True,  # LLM adds unverified street fair factor
            "unverified_surcharge_name": "Special city street fair exclusion zone surcharge",
            "unverified_surcharge_amount": 30.0
        },
        "vericore_scenario": {
            "scenario_name": "False Street Fair Surcharge Caught & Clamped",
            "description": "Pricing model proposes an ungrounded ₹30 festival surcharge. VeriCore live re-grounding queries municipal permit API, confirms no street closure exists, marks factor unsupported, and clamps price by ₹30.",
            "test_case_type": "Component 2 & 3 (Hallucination Catch)",
            "expected_adjustment": True,
            "expected_clamped_delta": 30.0
        }
    },
    {
        "lot_id": "lot-commercial-tower",
        "lot_name": "Prestige Commercial Plaza Deck",
        "zone": "Central Core",
        "address": "Residency Road, Bangalore 560025",
        "latitude": 12.9719,
        "longitude": 77.6012,
        "lot_type": "automated_robotic_stack",
        "total_spots": 250,
        "occupied_spots": 204,
        "spots_available": 46,
        "occupancy_rate": 0.816,
        "base_rate_per_hour": 40.0,
        "ev_charging_spots": 20,
        "handicap_spots": 8,
        "operating_hours": "24/7",
        "amenities": ["Automated Valet Stacker", "EV Superchargers", "Underground Security", "Restrooms"],
        "rating": 4.6,
        "cover_image_tone": "teal",
        "cover_asset": "/images/lots/lot-commercial-tower.svg",
        "distance_meters": 420,
        "walk_minutes": 5,
        "live_signals": {
            "occupancy_rate": 0.816,
            "nearby_event": "Tech Leaders Summit Day 2",
            "event_venue": "Grand Ballroom Residency",
            "event_distance_m": 350,
            "event_schedule_verified": True,
            "weather": "Clear",
            "weather_impact_multiplier": 1.0,
            "traffic_density": "Moderate (Level 2)",
            "traffic_sensor_id": "BLR-TRF-RES-02",
            "camera_feed_active": True,
            "camera_feed_id": "CAM-PRESTIGE-02",
            "camera_verified_available": 46,
            "sensor_discrepancy_flag": False,
            "unverified_surcharge_flag": False,
            "unverified_surcharge_name": None,
            "unverified_surcharge_amount": 0.0
        },
        "vericore_scenario": {
            "scenario_name": "Clean Multi-Factor Entailment Verification",
            "description": "Standard business hours peak. Occupancy and conference factors verified against live signals. Zero ungrounded factors. 100% verified.",
            "test_case_type": "Component 1 (Adaptive Multi-Tier Verification)",
            "expected_adjustment": False,
            "expected_clamped_delta": 0.0
        }
    },
    {
        "lot_id": "lot-civic-center",
        "lot_name": "Town Hall Civic Underground",
        "zone": "Civic Center",
        "address": "JC Road, Corporation Circle, Bangalore 560002",
        "latitude": 12.9634,
        "longitude": 77.5855,
        "lot_type": "underground_multi_level",
        "total_spots": 180,
        "occupied_spots": 108,
        "spots_available": 72,
        "occupancy_rate": 0.60,
        "base_rate_per_hour": 35.0,
        "ev_charging_spots": 8,
        "handicap_spots": 6,
        "operating_hours": "06:00 - 23:00",
        "amenities": ["Municipal Subsidized Rate", "CCTV Security", "Spacious Bays", "Wheelchair Ramps"],
        "rating": 4.3,
        "cover_image_tone": "amber",
        "cover_asset": "/images/lots/lot-civic-center.svg",
        "distance_meters": 750,
        "walk_minutes": 9,
        "live_signals": {
            "occupancy_rate": 0.60,
            "nearby_event": None,
            "event_venue": None,
            "event_distance_m": None,
            "event_schedule_verified": False,
            "weather": "Clear",
            "weather_impact_multiplier": 1.0,
            "traffic_density": "Low (Level 1)",
            "traffic_sensor_id": "BLR-TRF-JCR-01",
            "camera_feed_active": True,
            "camera_feed_id": "CAM-TOWNHALL-01",
            "camera_verified_available": 72,
            "sensor_discrepancy_flag": False,
            "unverified_surcharge_flag": False,
            "unverified_surcharge_name": None,
            "unverified_surcharge_amount": 0.0
        },
        "vericore_scenario": {
            "scenario_name": "Low Materiality Quick-Tier Verification",
            "description": "Off-peak civic lot with low occupancy. Base rate matches municipal tariff card. Fast, lightweight single-source check with latency < 40ms.",
            "test_case_type": "Component 1 (Light Tier Quick Check)",
            "expected_adjustment": False,
            "expected_clamped_delta": 0.0
        }
    },
    {
        "lot_id": "lot-express-deck",
        "lot_name": "Richmond Circle Automated Deck",
        "zone": "Central Core",
        "address": "Richmond Rd, Flyover Junction, Bangalore 560025",
        "latitude": 12.9667,
        "longitude": 77.5998,
        "lot_type": "automated_robotic_stack",
        "total_spots": 80,
        "occupied_spots": 52,
        "spots_available": 28,
        "occupancy_rate": 0.65,
        "base_rate_per_hour": 45.0,
        "ev_charging_spots": 6,
        "handicap_spots": 4,
        "operating_hours": "24/7",
        "amenities": ["Fast In-Out Turntable", "Mobile App Gate Unlock", "Covered Deck"],
        "rating": 4.5,
        "cover_image_tone": "teal",
        "cover_asset": "/images/lots/lot-express-deck.svg",
        "distance_meters": 950,
        "walk_minutes": 12,
        "live_signals": {
            "occupancy_rate": 0.65,
            "nearby_event": None,
            "event_venue": None,
            "event_distance_m": None,
            "event_schedule_verified": False,
            "weather": "Rain",
            "weather_impact_multiplier": 1.15,
            "traffic_density": "Moderate (Level 3)",
            "traffic_sensor_id": "BLR-TRF-RCH-03",
            "camera_feed_active": True,
            "camera_feed_id": "CAM-RICHMOND-01",
            "camera_verified_available": 28,
            "sensor_discrepancy_flag": False,
            "unverified_surcharge_flag": False,
            "unverified_surcharge_name": None,
            "unverified_surcharge_amount": 0.0
        },
        "vericore_scenario": {
            "scenario_name": "Rain Weather Surge Validation",
            "description": "Covered parking rain surge factor cross-checked against meteorological radar. Verified intact.",
            "test_case_type": "Component 1 (Standard Tier Careful Check)",
            "expected_adjustment": False,
            "expected_clamped_delta": 0.0
        }
    },
    {
        "lot_id": "lot-indiranagar-100ft",
        "lot_name": "Indiranagar 100ft Smart Vault",
        "zone": "Indiranagar",
        "address": "100 Feet Road, Near HAL 2nd Stage, Bangalore 560038",
        "latitude": 12.9784,
        "longitude": 77.6408,
        "lot_type": "automated_robotic_stack",
        "total_spots": 160,
        "occupied_spots": 146,
        "spots_available": 14,
        "occupancy_rate": 0.9125,
        "base_rate_per_hour": 45.0,
        "ev_charging_spots": 16,
        "handicap_spots": 6,
        "operating_hours": "24/7",
        "amenities": ["Automated Vault", "EV Fast Charging", "Valet Pickup", "ANPR Exit", "24/7 Guard"],
        "rating": 4.9,
        "cover_image_tone": "amber",
        "cover_asset": "/images/lots/lot-indiranagar.svg",
        "distance_meters": 220,
        "walk_minutes": 3,
        "live_signals": {
            "occupancy_rate": 0.9125,
            "nearby_event": "Weekend Live Music at Arena",
            "event_venue": "Indiranagar Arena Hall",
            "event_distance_m": 150,
            "event_schedule_verified": False, # Ended 2 hours ago!
            "weather": "Clear",
            "weather_impact_multiplier": 1.0,
            "traffic_density": "High (Level 4)",
            "traffic_sensor_id": "BLR-TRF-IND-01",
            "camera_feed_active": True,
            "camera_feed_id": "CAM-IND-VAULT-01",
            "camera_verified_available": 14,
            "sensor_discrepancy_flag": False,
            "unverified_surcharge_flag": True, # Event finished earlier
            "unverified_surcharge_name": "Weekend Music Venue Peak Surcharge",
            "unverified_surcharge_amount": 20.0
        },
        "vericore_scenario": {
            "scenario_name": "Stale Event Surge Removed by Live Re-Grounding",
            "description": "Event calendar listed an active concert, adding a ₹20 surcharge. Live municipal API re-check reveals the concert concluded at 4:30 PM. Factor flagged unsupported, price lowered from ₹130 to ₹110.",
            "test_case_type": "Component 2 (Live Re-Grounding Divergence)",
            "expected_adjustment": True,
            "expected_clamped_delta": 20.0
        }
    },
    {
        "lot_id": "lot-koramangala-nexus",
        "lot_name": "Koramangala Nexus Transit Plaza",
        "zone": "Koramangala",
        "address": "80 Feet Road, 4th Block Koramangala, Bangalore 560034",
        "latitude": 12.9344,
        "longitude": 77.6256,
        "lot_type": "underground_multi_level",
        "total_spots": 320,
        "occupied_spots": 210,
        "spots_available": 110,
        "occupancy_rate": 0.656,
        "base_rate_per_hour": 40.0,
        "ev_charging_spots": 24,
        "handicap_spots": 10,
        "operating_hours": "24/7",
        "amenities": ["Mall Internal Walkway", "EV 60kW DC Fast Charge", "Touchless Payment", "Car Wash Bay"],
        "rating": 4.7,
        "cover_image_tone": "teal",
        "cover_asset": "/images/lots/lot-koramangala.svg",
        "distance_meters": 310,
        "walk_minutes": 4,
        "live_signals": {
            "occupancy_rate": 0.656,
            "nearby_event": None,
            "event_venue": None,
            "event_distance_m": None,
            "event_schedule_verified": False,
            "weather": "Clear",
            "weather_impact_multiplier": 1.0,
            "traffic_density": "Moderate (Level 2)",
            "traffic_sensor_id": "BLR-TRF-KOR-02",
            "camera_feed_active": True,
            "camera_feed_id": "CAM-KOR-NEXUS-01",
            "camera_verified_available": 110,
            "sensor_discrepancy_flag": False,
            "unverified_surcharge_flag": False,
            "unverified_surcharge_name": None,
            "unverified_surcharge_amount": 0.0
        },
        "vericore_scenario": {
            "scenario_name": "Steady Moderate Retail Flow",
            "description": "Consistent retail shopping demand with verified EV fast charging status. Verified without adjustments.",
            "test_case_type": "Component 1 (Standard Tier)",
            "expected_adjustment": False,
            "expected_clamped_delta": 0.0
        }
    },
    {
        "lot_id": "lot-hospital-emergency",
        "lot_name": "Manipal Hospital Emergency & OPD Deck",
        "zone": "Hospital Zone",
        "address": "Old Airport Road, Kodihalli, Bangalore 560017",
        "latitude": 12.9592,
        "longitude": 77.6534,
        "lot_type": "surface_covered",
        "total_spots": 140,
        "occupied_spots": 122,
        "spots_available": 18,
        "occupancy_rate": 0.871,
        "base_rate_per_hour": 30.0,
        "ev_charging_spots": 4,
        "handicap_spots": 16,
        "operating_hours": "24/7",
        "amenities": ["Emergency Priority Bays", "Ambulance Right-of-Way", "Wheelchair Support", "24/7 Attendant"],
        "rating": 4.8,
        "cover_image_tone": "amber",
        "cover_asset": "/images/lots/lot-hospital.svg",
        "distance_meters": 110,
        "walk_minutes": 1,
        "live_signals": {
            "occupancy_rate": 0.871,
            "nearby_event": None,
            "event_venue": None,
            "event_distance_m": None,
            "event_schedule_verified": False,
            "weather": "Clear",
            "weather_impact_multiplier": 1.0,
            "traffic_density": "Emergency Corridor (Level 3)",
            "traffic_sensor_id": "BLR-TRF-MED-01",
            "camera_feed_active": True,
            "camera_feed_id": "CAM-MANIPAL-OPD",
            "camera_verified_available": 18,
            "sensor_discrepancy_flag": False,
            "unverified_surcharge_flag": True, # Hospital zone price gouging check
            "unverified_surcharge_name": "Peak emergency corridor priority surcharge",
            "unverified_surcharge_amount": 25.0
        },
        "vericore_scenario": {
            "scenario_name": "Healthcare Policy Invariant Enforcement",
            "description": "Dynamic pricing model generated a ₹25 surge in an emergency medical zone. VeriCore checks municipal healthcare parking regulations, finds surge pricing is strictly illegal in hospital zones, and clamps the price back to base statutory rate.",
            "test_case_type": "Component 3 (Policy Rule Invariant Clamping)",
            "expected_adjustment": True,
            "expected_clamped_delta": 25.0
        }
    },
    {
        "lot_id": "lot-whitefield-techpark",
        "lot_name": "ITPB International Tech Park Deck",
        "zone": "Tech Corridor",
        "address": "Whitefield Main Rd, Pattandur Agrahara, Bangalore 560066",
        "latitude": 12.9866,
        "longitude": 77.7375,
        "lot_type": "open_air_solar_canopy",
        "total_spots": 450,
        "occupied_spots": 395,
        "spots_available": 55,
        "occupancy_rate": 0.878,
        "base_rate_per_hour": 35.0,
        "ev_charging_spots": 40,
        "handicap_spots": 12,
        "operating_hours": "24/7",
        "amenities": ["Solar Canopy Shading", "40x EV Charging Points", "Shuttle to Metro", "Security Patrol"],
        "rating": 4.7,
        "cover_image_tone": "teal",
        "cover_asset": "/images/lots/lot-techpark.svg",
        "distance_meters": 350,
        "walk_minutes": 4,
        "live_signals": {
            "occupancy_rate": 0.878,
            "nearby_event": "Annual Developer Keynote",
            "event_venue": "ITPB Convention Hall",
            "event_distance_m": 200,
            "event_schedule_verified": True,
            "weather": "Clear",
            "weather_impact_multiplier": 1.0,
            "traffic_density": "Moderate (Level 3)",
            "traffic_sensor_id": "BLR-TRF-WFD-03",
            "camera_feed_active": True,
            "camera_feed_id": "CAM-ITPB-SOLAR-01",
            "camera_verified_available": 55,
            "sensor_discrepancy_flag": False,
            "unverified_surcharge_flag": False,
            "unverified_surcharge_name": None,
            "unverified_surcharge_amount": 0.0
        },
        "vericore_scenario": {
            "scenario_name": "Solar Tech Park Corporate Event Surge",
            "description": "Verified high weekday developer conference demand with solar canopy coverage. Factor verified across conference badge registry.",
            "test_case_type": "Component 1 (Deep Tier Live Entailment)",
            "expected_adjustment": False,
            "expected_clamped_delta": 0.0
        }
    }
]

def main():
    out_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Save Rich Hierarchical JSON
    json_path = os.path.join(out_dir, "veripark_smart_parking_dataset.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "dataset_name": "VeriPark Comprehensive Smart Parking Dataset",
                "version": "2.0.0",
                "geographic_region": "Bengaluru Metropolitan Area (BMA), India",
                "total_parking_facilities": len(SYNTHETIC_LOTS),
                "total_parking_bays": sum(l["total_spots"] for l in SYNTHETIC_LOTS),
                "total_ev_chargers": sum(l["ev_charging_spots"] for l in SYNTHETIC_LOTS),
                "currency": "INR",
                "assurance_engine": "VeriCore™ Materiality-Guided Verification & Clamping",
                "test_coverage": [
                    "Clean multi-factor verification",
                    "Hallucinated event surcharge detection & clamping",
                    "Sensor disparity and camera vision ground-truth check",
                    "Municipal tariff and policy invariant enforcement",
                    "Low-materiality quick checks vs high-materiality deep live queries"
                ]
            },
            "lots": SYNTHETIC_LOTS
        }, f, indent=2)
    print(f"Generated JSON dataset: {json_path}")

    # 2. Save Comprehensive Flat CSV
    csv_path = os.path.join(out_dir, "veripark_smart_parking_dataset.csv")
    csv_rows = []
    for lot in SYNTHETIC_LOTS:
        sig = lot["live_signals"]
        scen = lot["vericore_scenario"]
        csv_rows.append({
            "lot_id": lot["lot_id"],
            "lot_name": lot["lot_name"],
            "zone": lot["zone"],
            "address": lot["address"],
            "latitude": lot["latitude"],
            "longitude": lot["longitude"],
            "lot_type": lot["lot_type"],
            "total_spots": lot["total_spots"],
            "occupied_spots": lot["occupied_spots"],
            "spots_available": lot["spots_available"],
            "occupancy_rate_pct": round(lot["occupancy_rate"] * 100, 1),
            "base_rate_per_hour_inr": lot["base_rate_per_hour"],
            "ev_charging_spots": lot["ev_charging_spots"],
            "handicap_spots": lot["handicap_spots"],
            "operating_hours": lot["operating_hours"],
            "rating": lot["rating"],
            "amenities_list": "; ".join(lot["amenities"]),
            "distance_meters": lot["distance_meters"],
            "walk_minutes": lot["walk_minutes"],
            "weather_condition": sig["weather"],
            "traffic_density": sig["traffic_density"],
            "nearby_event_name": sig["nearby_event"] or "None",
            "nearby_event_venue": sig["event_venue"] or "N/A",
            "nearby_event_distance_m": sig["event_distance_m"] or 0,
            "nearby_event_verified": sig["event_schedule_verified"],
            "camera_feed_active": sig["camera_feed_active"],
            "camera_verified_available": sig["camera_verified_available"],
            "unverified_surcharge_detected": sig["unverified_surcharge_flag"],
            "unverified_surcharge_amount_inr": sig["unverified_surcharge_amount"],
            "vericore_scenario_name": scen["scenario_name"],
            "vericore_test_case_type": scen["test_case_type"],
            "expected_price_adjustment": scen["expected_adjustment"],
            "expected_clamped_delta_inr": scen["expected_clamped_delta"]
        })

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"Generated CSV dataset: {csv_path}")

if __name__ == "__main__":
    main()
