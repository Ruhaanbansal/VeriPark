"""Component 2 (Patent-Critical): Live Re-Grounding for High-Materiality Claims.

For claims routed to the 'deep' verification tier, VeriCore bypasses the
retrieval-time snapshot and issues a live query to the originating data source
(e.g. fresh camera vision count or live municipal API) at the moment of
verification. If the live measurement deviates beyond the configured tolerance,
the claim is flagged 'unsupported' and excluded from resummation.

Specification:
- Occupancy: defined as supported iff BOTH |live - claimed| <= occupancy_tolerance
  AND live >= surge_threshold.
- Event: supported iff active, schedule-verified, and distance <= event_radius_m.
- Weather: supported iff weather condition contains 'Rain'.
- Sensor-discrepancy: reads live camera count and live loop-detector count;
  unsupported only if camera > sensor beyond tolerance; otherwise supported.
- EV-premium: verified via lot registry check, not a live sensor (0 live queries issued).
- Unregistered / unknown types: unsupported with detail 'no live source registered for this factor type'
  (0 live queries issued).
- Timeouts & errors: fetch runs under timeout_seconds; on timeout or exception returns
  (False, 'unsupported', 'live source unavailable/timeout', 1); never raises.
"""

import concurrent.futures
from typing import Dict, Any, Tuple
from veripark.data_sources.parking_lots import fetch_live_data_source


def _fetch_with_timeout(
    lot_id: str,
    source_type: str,
    timeout_seconds: float
) -> Tuple[Dict[str, Any] | None, bool]:
    """Fetch live data source under a timeout constraint.

    Returns (fresh_data_dict, success_boolean).
    """
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fetch_live_data_source, lot_id, source_type)
            result = future.result(timeout=timeout_seconds)
            if isinstance(result, dict) and result.get("status") == "error":
                return None, False
            return result, True
    except Exception:
        return None, False


def reground_claim_live(
    lot_id: str,
    factor_id: str,
    claim_text: str,
    retrieved_context: Dict[str, Any] | None = None,
    tolerances: Dict[str, float] | None = None,
    rules: Dict[str, Any] | None = None,
    timeout_seconds: float | None = None,
) -> Tuple[bool, str, str, int]:
    """Issue a fresh live query to the originating data source.

    Args:
        lot_id:            Lot being evaluated.
        factor_id:         Factor ID (used for source dispatch, not claim-text matching).
        claim_text:        Original claim (retained for detail messages only).
        retrieved_context: Retrieval-time context dict (used to extract reference values
                           for tolerance comparison). If None, no comparison is done.
        tolerances:        Override tolerances dict.
        rules:             Domain rules dict (surge_threshold, event_radius_m).
        timeout_seconds:   Timeout in seconds for live queries.

    Returns:
        (is_supported, verdict, check_detail, live_query_count)
        live_query_count is 1 on every attempted source query (including timeouts),
        0 if factor_id is not a live-queryable type (handled by registry check or fail-closed).
    """
    if tolerances is None:
        try:
            from veripark.config import load_settings
            lr_cfg = load_settings().get("vericore", {}).get("live_regrounding", {})
            tolerances = {"occupancy_tolerance": lr_cfg.get("occupancy_tolerance", 0.08)}
        except Exception:
            tolerances = {"occupancy_tolerance": 0.08}

    occ_tol = tolerances.get("occupancy_tolerance", 0.08)

    if rules is None:
        try:
            from veripark.config import load_settings
            rules = load_settings().get("vericore", {}).get("rules", {})
        except Exception:
            rules = {}

    surge_threshold = rules.get("surge_threshold", 0.70)
    event_radius_m = rules.get("event_radius_m", 500)

    if timeout_seconds is None:
        try:
            from veripark.config import load_settings
            timeout_seconds = load_settings().get("vericore", {}).get("live_regrounding", {}).get("timeout_seconds", 3.0)
        except Exception:
            timeout_seconds = 3.0

    lot_ctx = (retrieved_context or {}).get("lot", {})
    cached_signals = lot_ctx.get("live_signals", {})

    # --- Dispatch by factor_id prefix (no claim-text matching) ---

    if factor_id.startswith("factor-occupancy"):
        fresh, ok = _fetch_with_timeout(lot_id, "occupancy", timeout_seconds)
        if not ok or fresh is None:
            return (
                False,
                "unsupported",
                "live source unavailable/timeout",
                1,
            )

        live_occ = fresh.get("live_occupancy_rate", 0.0)
        spots_left = fresh.get("live_spots_available", 0)
        cached_occ = cached_signals.get("occupancy_rate", live_occ)

        diff = abs(live_occ - cached_occ)
        # Supported iff BOTH |live - claimed| <= occupancy_tolerance AND live >= surge_threshold
        if diff <= occ_tol and live_occ >= surge_threshold:
            return (
                True,
                "live_reverified",
                f"Rechecked live just now: camera stream confirmed {spots_left} spots remaining "
                f"({int(live_occ*100)}% occupancy).",
                1,
            )
        elif diff > occ_tol:
            return (
                False,
                "unsupported",
                f"Live re-check: occupancy diverged from cache ({int(cached_occ*100)}% cached, "
                f"{int(live_occ*100)}% live) beyond tolerance {int(occ_tol*100)}%.",
                1,
            )
        else:
            return (
                False,
                "unsupported",
                f"Live re-check: camera feed reported occupancy dropped to {int(live_occ*100)}%, "
                f"below surge threshold ({int(surge_threshold * 100)}%).",
                1,
            )

    elif factor_id.startswith("factor-event"):
        fresh, ok = _fetch_with_timeout(lot_id, "event", timeout_seconds)
        if not ok or fresh is None:
            return (
                False,
                "unsupported",
                "live source unavailable/timeout",
                1,
            )

        is_active = fresh.get("event_active", False)
        raw_dist = fresh.get("event_distance_m")
        dist = float(raw_dist) if raw_dist is not None else None
        verified = fresh.get("event_schedule_verified", False)

        if is_active and verified and dist is not None and dist <= event_radius_m:
            return (
                True,
                "live_reverified",
                f"Rechecked live just now: city events feed confirmed "
                f"'{fresh.get('event_name')}' active {dist}m away and schedule verified.",
                1,
            )
        reason_parts = []
        if not is_active:
            reason_parts.append("event not found in live feed")
        if not verified:
            reason_parts.append("schedule not verified")
        if dist is None:
            reason_parts.append("event distance unavailable")
        elif dist > event_radius_m:
            reason_parts.append(f"event is {dist}m away (>{event_radius_m}m radius)")
        return (
            False,
            "unsupported",
            "Live re-check failed: " + "; ".join(reason_parts) + ".",
            1,
        )

    elif factor_id.startswith("factor-weather"):
        fresh, ok = _fetch_with_timeout(lot_id, "weather", timeout_seconds)
        if not ok or fresh is None:
            return (
                False,
                "unsupported",
                "live source unavailable/timeout",
                1,
            )

        cond = fresh.get("weather_condition", "")
        if "Rain" in cond:
            return (
                True,
                "live_reverified",
                "Rechecked live just now: meteorological radar confirms active precipitation advisory.",
                1,
            )
        return (
            False,
            "unsupported",
            f"Live re-check failed: weather radar reports '{cond}' — no active rain advisory.",
            1,
        )

    elif factor_id.startswith("factor-sensor-discrepancy"):
        fresh, ok = _fetch_with_timeout(lot_id, "occupancy", timeout_seconds)
        if not ok or fresh is None:
            return (
                False,
                "unsupported",
                "live source unavailable/timeout",
                1,
            )

        camera_count = fresh.get("camera_verified_available")
        if camera_count is None:
            camera_count = fresh.get("live_spots_available")
        sensor_count = fresh.get("sensor_reported_available")

        if camera_count is not None and sensor_count is not None:
            sensor_tol = tolerances.get("sensor_tolerance", 0)
            if camera_count > sensor_count + sensor_tol:
                return (
                    False,
                    "unsupported",
                    f"Live camera re-check: overhead vision stream confirmed {camera_count} spaces free "
                    f"vs loop-detector's {sensor_count} — loop-detector over-reported congestion. "
                    "Conservative demand premium removed.",
                    1,
                )
            else:
                return (
                    True,
                    "live_reverified",
                    f"Live camera re-check: overhead vision stream confirmed {camera_count} spaces free "
                    f"<= loop-detector's {sensor_count}. Discrepancy confirmed.",
                    1,
                )
        return (
            False,
            "unsupported",
            "Live sensor readings unavailable for discrepancy comparison.",
            1,
        )

    elif factor_id.startswith("factor-ev-premium"):
        # EV premium is verified from lot registry data, not a live sensor feed (0 queries)
        ev_spots = lot_ctx.get("ev_charging_spots")
        if ev_spots is None:
            from veripark.data_sources.parking_lots import PARKING_LOTS_DB
            ev_spots = PARKING_LOTS_DB.get(lot_id, {}).get("ev_charging_spots", 0)

        if ev_spots and ev_spots > 0:
            return (
                True,
                "live_reverified",
                f"registry check, not a live sensor: confirmed {ev_spots} EV bays",
                0,
            )
        return (
            False,
            "unsupported",
            "registry check, not a live sensor: no EV bays recorded for lot",
            0,
        )

    else:
        # unverified / festival / emergency IDs or unknown factor types:
        # No live source registered for them. Return unsupported with 0 queries.
        return (
            False,
            "unsupported",
            "no live source registered for this factor type",
            0,
        )
