import pytest
from veripark.vericore.decision_resummation import resum_decision

class DummyFactor:
    def __init__(self, factor_id: str, contribution: float, description: str = ""):
        self.factor_id = factor_id
        self.contribution = contribution
        self.description = description

class DummyPricingResult:
    def __init__(self, base_price: float, proposed_price: float, factors: list):
        self.base_price = base_price
        self.proposed_price = proposed_price
        self.factors = factors

class DummyClaimVerdict:
    def __init__(self, factor_id: str, verdict: str):
        self.factor_id = factor_id
        self.verdict = verdict

def test_invariant_final_price_never_exceeds_proposed():
    """Invariant 1: final_price must NEVER exceed proposed_price under any circumstance."""
    factors = [
        DummyFactor("f1", 30.0),
        DummyFactor("f2", 20.0),
    ]
    # base 100 + sum 50 = 150. Even if proposed was artificially set lower (e.g. 140), min clamps it
    pricing = DummyPricingResult(base_price=100.0, proposed_price=140.0, factors=factors)
    verdicts = [
        DummyClaimVerdict("f1", "supported"),
        DummyClaimVerdict("f2", "supported"),
    ]
    res = resum_decision(pricing, verdicts)
    assert res["final_price"] <= pricing.proposed_price
    assert res["final_price"] == 140.0

def test_invariant_binary_factor_inclusion():
    """Invariant 2: Factor inclusion is binary (no partial credit).
    Unsupported factors must be excluded completely.
    """
    factors = [
        DummyFactor("f_occ", 35.0),
        DummyFactor("f_event", 25.0),
        DummyFactor("f_hallucinated", 40.0)
    ]
    pricing = DummyPricingResult(base_price=100.0, proposed_price=200.0, factors=factors)
    verdicts = [
        DummyClaimVerdict("f_occ", "supported"),
        DummyClaimVerdict("f_event", "live_reverified"),
        DummyClaimVerdict("f_hallucinated", "unsupported")
    ]
    res = resum_decision(pricing, verdicts)
    # base 100 + 35 + 25 = 160. f_hallucinated (40) excluded completely.
    assert res["final_price"] == 160.0
    assert res["delta"] == 40.0
    assert res["was_adjusted"] is True
    assert "f_hallucinated" in res["excluded_factors"]
    assert "f_occ" not in res["excluded_factors"]

def test_resummation_all_supported():
    """When all factors are supported, final_price equals proposed_price and was_adjusted is False."""
    factors = [
        DummyFactor("f1", 20.0),
        DummyFactor("f2", 15.0)
    ]
    pricing = DummyPricingResult(base_price=50.0, proposed_price=85.0, factors=factors)
    verdicts = [
        DummyClaimVerdict("f1", "supported"),
        DummyClaimVerdict("f2", "supported")
    ]
    res = resum_decision(pricing, verdicts)
    assert res["final_price"] == 85.0
    assert res["delta"] == 0.0
    assert res["was_adjusted"] is False
    assert len(res["excluded_factors"]) == 0
