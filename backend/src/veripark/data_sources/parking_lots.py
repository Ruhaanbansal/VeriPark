import os
import json
import time
import random
from typing import Dict, Any, List, Optional

# Load from synthetic dataset
POSSIBLE_PATHS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "synthetic", "veripark_smart_parking_dataset.json")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "synthetic", "veripark_smart_parking_dataset.json")),
    os.path.abspath(os.path.join(os.getcwd(), "data", "synthetic", "veripark_smart_parking_dataset.json")),
]

DATASET_PATH = next((p for p in POSSIBLE_PATHS if os.path.exists(p)), POSSIBLE_PATHS[0])

PARKING_LOTS_DB: Dict[str, Dict[str, Any]] = {}

def _init_lots():
    global PARKING_LOTS_DB
    if os.path.exists(DATASET_PATH):
        try:
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("lots", []):
                    lid = item["lot_id"]
                    PARKING_LOTS_DB[lid] = {
                        "id": lid,
                        "name": item["lot_name"],
                        "zone": item["zone"],
                        "address": item["address"],
                        "latitude": item.get("latitude", 12.9716),
                        "longitude": item.get("longitude", 77.5946),
                        "lot_type": item.get("lot_type", "underground_multi_level"),
                        "distance_meters": item.get("distance_meters", 300),
                        "walk_minutes": item.get("walk_minutes", 4),
                        "total_spots": item["total_spots"],
                        "spots_available": item["spots_available"],
                        "base_rate_per_hour": item["base_rate_per_hour"],
                        "ev_charging_spots": item.get("ev_charging_spots", 8),
                        "handicap_spots": item.get("handicap_spots", 4),
                        "rating": item.get("rating", 4.6),
                        "cover_image_tone": item.get("cover_image_tone", "amber"),
                        "cover_asset": item.get("cover_asset", "/images/lots/lot-metro-hub.svg"),
                        "amenities": item.get("amenities", []),
                        "operating_hours": item.get("operating_hours", "24/7"),
                        "live_signals": item.get("live_signals", {}),
                        "vericore_scenario": item.get("vericore_scenario", {})
                    }
        except Exception as e:
            print(f"Warning: could not load synthetic dataset from {DATASET_PATH}: {e}")

_init_lots()

def query_lots(destination: str) -> List[Dict[str, Any]]:
    """Return candidate lots for a destination query."""
    if not PARKING_LOTS_DB:
        _init_lots()
    dest_lower = destination.strip().lower()
    lots = list(PARKING_LOTS_DB.values())
    if not dest_lower or dest_lower in ["all", "bangalore", "any", "city"]:
        return lots
    # Prioritize matching zone or name
    matched = [l for l in lots if dest_lower in l["zone"].lower() or dest_lower in l["name"].lower() or dest_lower in l["address"].lower()]
    return matched if matched else lots

def get_lot_by_id(lot_id: str) -> Optional[Dict[str, Any]]:
    if not PARKING_LOTS_DB:
        _init_lots()
    return PARKING_LOTS_DB.get(lot_id)

def fetch_live_data_source(lot_id: str, claim_type: str) -> Dict[str, Any]:
    """Component 2 (Live Re-Grounding origin query):
    Directly query originating sensors/APIs, bypassing cache.
    """
    lot = PARKING_LOTS_DB.get(lot_id)
    if not lot:
        return {"status": "error", "message": "Lot not found"}
    
    signals = lot["live_signals"]
    timestamp = time.time()
    
    if claim_type == "occupancy":
        # Direct camera vision count re-poll
        return {
            "type": "occupancy",
            "live_occupancy_rate": signals["occupancy_rate"],
            "live_spots_available": signals["camera_verified_available"],
            "total_spots": lot["total_spots"],
            "source": "live_overhead_edge_camera_stream_rtsp_01",
            "timestamp": timestamp,
            "freshness_ms": 140
        }
    elif claim_type == "event":
        return {
            "type": "event",
            "event_active": signals.get("nearby_event") is not None,
            "event_name": signals.get("nearby_event"),
            "event_distance_m": signals.get("event_distance_m"),
            "event_schedule_verified": signals.get("event_schedule_verified", True),
            "source": "city_events_api_v2_live",
            "timestamp": timestamp,
            "freshness_ms": 320
        }
    elif claim_type == "weather":
        return {
            "type": "weather",
            "weather_condition": signals["weather"],
            "source": "meteorological_radar_live",
            "timestamp": timestamp,
            "freshness_ms": 210
        }
    elif claim_type == "traffic":
        return {
            "type": "traffic",
            "traffic_density": signals["traffic_density"],
            "source": "municipal_traffic_sensor_mesh",
            "timestamp": timestamp,
            "freshness_ms": 180
        }
    else:
        return {
            "type": "generic",
            "valid": True,
            "source": "live_sensor_gateway",
            "timestamp": timestamp
        }
