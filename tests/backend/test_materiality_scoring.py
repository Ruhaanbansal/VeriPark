import pytest
from veripark.vericore.materiality_scoring import compute_claim_materiality
from veripark.vericore.adaptive_routing import route_claim

def test_materiality_exact_formula():
    # proposed: 180, base: 100 -> delta = 80
    # factor contrib: 40 -> materiality = 40 / 80 = 0.50
    mat = compute_claim_materiality(
        factor_contribution=40.0,
        proposed_price=180.0,
        base_price=100.0,
        epsilon=1e-6
    )
    assert mat == pytest.approx(0.50, rel=1e-4)

def test_materiality_small_delta_epsilon_handling():
    # proposed == base -> delta = 0 -> denominator = epsilon
    mat = compute_claim_materiality(
        factor_contribution=0.0,
        proposed_price=100.0,
        base_price=100.0,
        epsilon=1e-6
    )
    assert mat == 0.0

def test_adaptive_routing_tiers():
    # < 0.10 -> light
    assert route_claim(0.05, 0.10, 0.40) == "light"
    assert route_claim(0.099, 0.10, 0.40) == "light"

    # 0.10 to 0.40 -> standard
    assert route_claim(0.10, 0.10, 0.40) == "standard"
    assert route_claim(0.25, 0.10, 0.40) == "standard"
    assert route_claim(0.399, 0.10, 0.40) == "standard"

    # >= 0.40 -> deep (escalated to live re-grounding)
    assert route_claim(0.40, 0.10, 0.40) == "deep"
    assert route_claim(0.75, 0.10, 0.40) == "deep"
