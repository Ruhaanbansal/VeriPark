"""Component 2 support: LiveStateStore and DriftInjector.

Provides a per-lot live state layer on top of the dataset snapshot.
Default: no overrides, so behaviour is identical to the current snapshot.
Used by fetch_live_data_source to separate live queries from retrieval cache.
"""

import threading
import random
from typing import Any, Dict, Optional


class LiveStateStore:
    """Thread-safe store of per-lot field overrides on top of the dataset snapshot.

    Default: get_field returns None (caller falls back to snapshot value).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._overrides: Dict[str, Dict[str, Any]] = {}

    def set_override(self, lot_id: str, field: str, value: Any) -> None:
        """Set a live override for a specific lot field."""
        with self._lock:
            if lot_id not in self._overrides:
                self._overrides[lot_id] = {}
            self._overrides[lot_id][field] = value

    def get_field(self, lot_id: str, field: str) -> Optional[Any]:
        """Return override value if set, else None (caller uses snapshot)."""
        with self._lock:
            return self._overrides.get(lot_id, {}).get(field)

    def clear(self, lot_id: Optional[str] = None) -> None:
        """Clear overrides for a specific lot or all lots."""
        with self._lock:
            if lot_id is None:
                self._overrides.clear()
            else:
                self._overrides.pop(lot_id, None)


class DriftInjector:
    """Injects controlled perturbations into live state to simulate sensor drift.

    Applies perturbations to the live store after retrieval. Seeded for
    reproducibility. Perturbation types:
    - occupancy_shift: add ±fraction to occupancy_rate (clamped 0..1)
    - event_cancel: set event_schedule_verified=False (simulates stale event)
    - weather_clear: clear rain condition

    Usage:
        injector = DriftInjector(fraction=0.10, seed=42)
        injector.apply(live_store, lot_id)
    """

    def __init__(self, fraction: float = 0.0, seed: int = 0) -> None:
        self.fraction = fraction
        self.rng = random.Random(seed)

    def apply(self, store: LiveStateStore, lot_id: str, snapshot: Dict[str, Any]) -> None:
        """Perturb live state for lot_id based on the snapshot values."""
        if self.fraction <= 0.0:
            return

        signals = snapshot.get("live_signals", {})

        # Occupancy drift
        if self.rng.random() < self.fraction:
            base_occ = signals.get("occupancy_rate", 0.5)
            shift = self.rng.uniform(-self.fraction, self.fraction)
            new_occ = max(0.0, min(1.0, base_occ + shift))
            store.set_override(lot_id, "occupancy_rate", new_occ)

        # Event cancellation drift
        if signals.get("nearby_event") and self.rng.random() < self.fraction:
            store.set_override(lot_id, "event_schedule_verified", False)

        # Weather clearing drift
        if "Rain" in signals.get("weather", "") and self.rng.random() < self.fraction:
            store.set_override(lot_id, "weather", "Clear")


# Module-level singleton: default has no overrides (no behaviour change)
_live_store = LiveStateStore()


def get_live_store() -> LiveStateStore:
    """Return the module-level LiveStateStore singleton."""
    return _live_store
