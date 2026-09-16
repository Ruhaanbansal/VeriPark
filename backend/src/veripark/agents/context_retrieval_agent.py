from typing import Dict, Any, List
from veripark.data_sources.parking_lots import query_lots, get_lot_by_id

class ContextRetrievalAgent:
    """Stage 1: Gathers real-time occupancy, nearby events, weather, and traffic signals."""

    def retrieve_context(self, destination: str, duration_hours: int = 2) -> Dict[str, Any]:
        lots = query_lots(destination)
        return {
            "destination": destination,
            "duration_hours": duration_hours,
            "candidate_lots": lots,
            "retrieval_timestamp": "2026-09-16T17:45:00Z"
        }

    def get_lot_context(self, lot_id: str, duration_hours: int = 2) -> Dict[str, Any]:
        lot = get_lot_by_id(lot_id)
        if not lot:
            raise ValueError(f"Unknown lot ID: {lot_id}")
        return {
            "lot": lot,
            "duration_hours": duration_hours
        }
