"""Component 1 (Patent-Critical): Decision-Materiality Scoring.

Computes, for every extracted claim, a materiality score:
a counterfactual estimate of how much the final price rests on that specific claim.

Formula:
materiality(claim) = abs(factor.contribution) / max(abs(proposed_price - base_price), epsilon)
"""

def compute_claim_materiality(
    factor_contribution: float,
    proposed_price: float,
    base_price: float,
    epsilon: float = 1e-6
) -> float:
    """Calculate the exact materiality score of a claim/factor.

    Represents the proportion of total price adjustment that rests
    on this individual claim.
    """
    price_delta = abs(proposed_price - base_price)
    denominator = max(price_delta, epsilon)
    score = abs(factor_contribution) / denominator
    return round(float(score), 6)
