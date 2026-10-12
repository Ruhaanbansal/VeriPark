"""Protocol interfaces for VeriCore™ verification extensions.

Defines structural subtyping protocols for pluggable Entailment Verifiers
and Claim Judges without imposing heavyweight ML dependencies on core.
"""

from typing import Protocol, Dict, Any, Tuple, runtime_checkable

@runtime_checkable
class EntailmentVerifier(Protocol):
    """Protocol for rule-based, NLI cross-encoder, or LLM entailment verification."""
    def verify(self, claim: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, str]:
        """Verifies if the claim is entailed by the retrieved context."""
        ...

@runtime_checkable
class ClaimJudge(Protocol):
    """Protocol for live data-source re-grounding and claim arbitration."""
    def judge(self, claim: Dict[str, Any], live_source_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Arbitrates if live sensor/API observations substantiate the claim."""
        ...
