import os
from pathlib import Path
import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "settings.yaml"

def load_settings(config_path: Path | str | None = None) -> dict:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        # Fallback to local settings structure if file missing
        return {
            "vericore": {
                "materiality": {"epsilon": 1e-6, "light_threshold": 0.10, "standard_threshold": 0.40},
                "routing": {"tiers": ["light", "standard", "deep"]},
                "rules": {"surge_threshold": 0.70, "event_radius_m": 500},
                "live_regrounding": {"occupancy_tolerance": 0.08, "rate_tolerance": 5.0},
                "resummation": {"enforce_clamping_invariant": True, "allow_partial_credit": False},
                "ledger": {"file_path": "data/ledger/ledger.jsonl", "hash_algorithm": "sha256"},
            },
            "server": {"host": "127.0.0.1", "port": 8000}
        }
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
