"""Component 1 (Patent-Critical): Adaptive Verification Routing.

Routes claim verification depth in proportion to decision consequence (materiality),
NOT model uncertainty.

Routing tiers:
- 'light' (< light_threshold, e.g. 0.10): Fast entailment check.
- 'standard' (< standard_threshold, e.g. 0.40): Entailment + LLM structured judge.
- 'deep' (>= standard_threshold): Deep verification + live re-grounding against source sensors.
"""

from typing import Literal

VerificationTier = Literal["light", "standard", "deep"]

def route_claim(
    materiality: float,
    light_threshold: float = 0.10,
    standard_threshold: float = 0.40
) -> VerificationTier:
    """Route a claim to a verification tier based strictly on materiality."""
    if materiality < light_threshold:
        return "light"
    elif materiality < standard_threshold:
        return "standard"
    else:
        return "deep"
