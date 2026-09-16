"""Friendly label mappings for VeriPark API.

Ensures no internal/patent-sensitive vocabulary (tier enums, verdict enums)
leaks to client-visible payloads.
"""

TIER_LABELS = {
    "light": "Quick check",
    "standard": "Careful check",
    "deep": "Rechecked live just now",
}

VERDICT_LABELS = {
    "supported": "Verified",
    "unsupported": "Excluded — couldn't be verified",
    "live_reverified": "Verified against live data",
}

def to_friendly_tier(tier: str) -> str:
    return TIER_LABELS.get(tier.lower(), "Checked")

def to_friendly_verdict(verdict: str) -> str:
    return VERDICT_LABELS.get(verdict.lower(), "Verified")
