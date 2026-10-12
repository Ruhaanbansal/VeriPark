"""Structured evidence assessment for NLI and structured verification.

Uses a registry of known factor types. Unknown or unverifiable factor IDs
fail-closed (return False) rather than defaulting to supported.
"""

from typing import Dict, Any, Tuple

# Registry of factor ID prefixes/patterns that have known verification rules.
# Any factor_id that does NOT match a known prefix is fail-closed (unsupported).
_KNOWN_PREFIXES = (
    "factor-occupancy",
    "factor-event",
    "factor-weather",
    "factor-ev-premium",
    "factor-sensor-discrepancy",
)

def _is_known_factor(factor_id: str) -> bool:
    """Return True only if the factor has a defined evidence rule."""
    return any(factor_id.startswith(p) for p in _KNOWN_PREFIXES)


def evaluate_evidence_entailment(
    claim_text: str,
    factor_id: str,
    retrieved_context: Dict[str, Any],
    rules: Dict[str, Any] | None = None,
) -> Tuple[bool, str]:
    """Lightweight evidence entailment evaluation against cached context.

    Verifies that the claim is entailed by retrieved context data.
    Fail-closed: unknown or unregistered factor IDs return unsupported so that
    the resummation engine conservatively excludes them.

    Note: keyword matching on claim_text is intentionally NOT used here.
    All routing is done on factor_id only to prevent prompt-injection bypass.
    """
    if rules is None:
        try:
            from veripark.config import load_settings
            rules = load_settings().get("vericore", {}).get("rules", {})
        except Exception:
            rules = {}

    surge_threshold = rules.get("surge_threshold", 0.70)
    event_radius_m = rules.get("event_radius_m", 500)

    lot = retrieved_context.get("lot", {})
    signals = lot.get("live_signals", {})

    # --- Fail-closed gate: unknown factor types are never supported ---
    if not _is_known_factor(factor_id):
        return (
            False,
            f"No evidence rule for factor type '{factor_id}'; "
            "treating as unsupported per fail-closed policy."
        )

    # --- factor-occupancy ---
    if factor_id.startswith("factor-occupancy"):
        occ = signals.get("occupancy_rate", 0.0)
        if occ >= surge_threshold:
            return True, f"Entailment confirmed: cached occupancy was {int(occ * 100)}%."
        return False, f"Occupancy in cached context was below surge threshold ({int(surge_threshold * 100)}%)."

    # --- factor-event ---
    if factor_id.startswith("factor-event"):
        event = signals.get("nearby_event")
        if not event:
            return False, "No nearby event found in cached context."
        # C2 integrity gate: if the event schedule is not verified in the cache,
        # fail at this tier — a live re-grounding call is required.
        if not signals.get("event_schedule_verified", False):
            return (
                False,
                f"Event '{event}' in cache but schedule_verified=False; "
                "cannot entail without live confirmation."
            )
        dist = signals.get("event_distance_m")
        if dist is not None and dist > event_radius_m:
            return (
                False,
                f"Event '{event}' is {dist}m away (>{event_radius_m}m radius)."
            )
        return True, f"Entailment confirmed: cached event '{event}' is verified active."

    # --- factor-weather ---
    if factor_id.startswith("factor-weather"):
        weather = signals.get("weather", "")
        if "Rain" in weather:
            return True, "Entailment confirmed: precipitation alert in cached context."
        return False, "Weather in cached context does not warrant rain premium."

    # --- factor-ev-premium ---
    if factor_id.startswith("factor-ev-premium"):
        ev_spots = lot.get("ev_charging_spots", 0)
        if ev_spots > 0:
            return True, f"Entailment confirmed: {ev_spots} EV charging spots in lot registry."
        return False, "No EV charging spots recorded for this lot."

    # --- factor-sensor-discrepancy ---
    if factor_id.startswith("factor-sensor-discrepancy"):
        camera_count = signals.get("camera_verified_available")
        sensor_count = signals.get("sensor_reported_available")
        if camera_count is not None and sensor_count is not None:
            # Camera is ground truth; if camera shows more spaces than sensor reported,
            # the conservative demand premium is not supported.
            if camera_count > sensor_count:
                return (
                    False,
                    f"Camera confirms {camera_count} spaces free vs loop-detector's "
                    f"{sensor_count}; conservative demand premium is unsupported."
                )
        # If we cannot determine a discrepancy from cache, fail-closed.
        return (
            False,
            "Sensor discrepancy factor cannot be confirmed from cached context alone; "
            "treating as unsupported per fail-closed policy."
        )

    # Should not be reached due to _is_known_factor gate above.
    return False, "Unhandled known factor type — treating as unsupported."
