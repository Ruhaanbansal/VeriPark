"""Ground-truth factor validity determination for empirical evaluation.

Independent of the verifier code. Evaluates whether a proposed pricing factor
is factually valid according to the world state (live state after drift).

Specification:
- occupancy: valid iff |live - claimed| <= occupancy_tolerance and live >= surge_threshold;
- event: valid iff event exists in live state, is schedule-verified, and is within event_radius_m;
- weather: valid iff live weather contains 'Rain';
- ev-premium: valid iff the lot has EV bays (> 0);
- sensor-discrepancy: valid iff camera <= sensor beyond tolerance would NOT be violated,
  i.e. invalid when camera count exceeds loop-detector count (camera is ground truth);
- any factor whose type has no rule, or that was injected as a phantom, is invalid.
"""

from typing import Dict, Any, Optional


def is_factor_ground_truth_valid(
    factor: Dict[str, Any],
    lot: Dict[str, Any],
    live_signals: Dict[str, Any],
    claimed_signals: Dict[str, Any],
    is_phantom: bool = False,
    rules: Optional[Dict[str, Any]] = None,
    tolerances: Optional[Dict[str, Any]] = None,
) -> bool:
    """Determine whether a pricing factor is valid under the world state.

    Args:
        factor:           Factor dictionary containing 'factor_id' and 'contribution'.
        lot:              Lot dictionary containing registry fields (e.g. ev_charging_spots).
        live_signals:     Effective live signals in the world state (after any drift injection).
        claimed_signals:  Snapshot signals claimed/retrieved at proposal time.
        is_phantom:       Whether this factor was injected as an artificial phantom.
        rules:            Domain rules dict (surge_threshold, event_radius_m).
        tolerances:       Live regrounding tolerances dict (occupancy_tolerance, sensor_tolerance).

    Returns:
        True if the factor is grounded and factually valid in the world state; False otherwise.
    """
    if is_phantom:
        return False

    fid = factor.get("factor_id", "")

    if rules is None:
        try:
            from veripark.config import load_settings
            rules = load_settings().get("vericore", {}).get("rules", {})
        except Exception:
            rules = {}

    surge_threshold = rules.get("surge_threshold", 0.70)
    event_radius_m = rules.get("event_radius_m", 500)

    if tolerances is None:
        try:
            from veripark.config import load_settings
            tolerances = load_settings().get("vericore", {}).get("live_regrounding", {})
        except Exception:
            tolerances = {}

    occ_tol = tolerances.get("occupancy_tolerance", 0.08)
    sensor_tol = tolerances.get("sensor_tolerance", 0)

    # 1. Occupancy factor
    if fid.startswith("factor-occupancy"):
        live_occ = live_signals.get("occupancy_rate", 0.0)
        claimed_occ = claimed_signals.get("occupancy_rate", live_occ)
        diff = abs(live_occ - claimed_occ)
        return (diff <= occ_tol) and (live_occ >= surge_threshold)

    # 2. Event proximity factor
    elif fid.startswith("factor-event"):
        event_name = live_signals.get("nearby_event")
        if not event_name:
            return False
        schedule_verified = bool(live_signals.get("event_schedule_verified", False))
        if not schedule_verified:
            return False
        raw_dist = live_signals.get("event_distance_m")
        if raw_dist is None:
            return False
        try:
            dist = float(raw_dist)
        except (ValueError, TypeError):
            return False
        return dist <= event_radius_m

    # 3. Weather adjustment
    elif fid.startswith("factor-weather"):
        weather = str(live_signals.get("weather", ""))
        return "Rain" in weather

    # 4. EV premium
    elif fid.startswith("factor-ev-premium"):
        ev_spots = lot.get("ev_charging_spots", 0)
        return ev_spots > 0

    # 5. Sensor disparity
    elif fid.startswith("factor-sensor-discrepancy"):
        cam = live_signals.get("camera_verified_available")
        sensor = live_signals.get("sensor_reported_available")
        if cam is not None and sensor is not None:
            # Camera is ground truth. Invalid if camera exceeds sensor beyond tolerance.
            return not (cam > sensor + sensor_tol)
        return False

    # Any factor whose type has no rule (or unknown prefix) is invalid
    return False
