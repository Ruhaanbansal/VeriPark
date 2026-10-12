"""End-to-End VeriPark Pipeline integrating Agents with the VeriCore™ Assurance Engine."""

import time
import uuid
from typing import Dict, Any, List, Optional
from veripark.agents.context_retrieval_agent import ContextRetrievalAgent
from veripark.agents.allocation_pricing_agent import AllocationPricingAgent
from veripark.agents.explanation_drafting_agent import ExplanationDraftingAgent
from veripark.vericore.claim_extraction import extract_and_bind_claims
from veripark.vericore.faithfulness_scoring import verify_claims_cascade
from veripark.vericore.decision_resummation import resum_decision
from veripark.vericore.ledger import DecisionLedger
from veripark.config import load_settings

class VeriParkPipeline:
    def __init__(self, config: Optional[Dict[str, Any]] = None, ledger_path: Optional[str] = None):
        self.config = config or load_settings()
        self.retrieval_agent = ContextRetrievalAgent()
        self.pricing_agent = AllocationPricingAgent()
        self.drafting_agent = ExplanationDraftingAgent()
        
        lp = ledger_path or self.config.get("vericore", {}).get("ledger", {}).get("file_path")
        self.ledger = DecisionLedger(file_path=lp)

    def process_decision(
        self,
        lot_id: str,
        duration_hours: int = 2,
        decision_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs the complete 5-stage VeriPark pipeline.

        1. Context Retrieval Agent
        2. Allocation & Pricing Agent
        3. Explanation Drafting Agent
        4. VeriCore™ Assurance Engine:
           - Component 1: Materiality Scoring & Adaptive Routing
           - Component 2: Live Re-Grounding for deep tier
           - Component 3: Self-Correcting Decision Clamping / Resummation
           - Component 4: Verifiable Ledger sealing
        """
        if not decision_id:
            decision_id = f"dec-{uuid.uuid4().hex[:10]}"

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Stage 1: Context Retrieval
        lot_context = self.retrieval_agent.get_lot_context(lot_id, duration_hours=duration_hours)

        # Stage 2: Allocation & Pricing
        pricing_result = self.pricing_agent.propose_pricing(lot_context)

        # Stage 3: Explanation Drafting (provenance-tagged claims)
        draft_claims = self.drafting_agent.draft_explanation(pricing_result, lot_context)

        # Stage 4: VeriCore Assurance Engine
        # 4a: Extract & Bind Claims
        bound_claims = extract_and_bind_claims(draft_claims, pricing_result["factors"])

        # 4b: Materiality-Weighted Verification Cascade (Components 1 & 2)
        verdicts, verification_metrics = verify_claims_cascade(
            bound_claims, pricing_result, lot_context, self.config
        )

        # 4c: Decision Resummation / Clamping (Component 3)
        resummation = resum_decision(pricing_result, verdicts)

        # Stage 5: Seal into Verifiable Ledger (Component 4)
        verdict_dicts = [v.model_dump() for v in verdicts]
        ledger_entry = self.ledger.record_decision(
            decision_id=decision_id,
            lot_id=lot_id,
            pricing_result=pricing_result,
            resummation_result=resummation,
            claim_verdicts=verdict_dicts,
            timestamp=timestamp
        )

        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "lot_id": lot_id,
            "lot": lot_context["lot"],
            "duration_hours": duration_hours,
            "pricing_result": pricing_result,
            "bound_claims": bound_claims,
            "verdicts": verdicts,
            "resummation": resummation,
            "ledger_entry": ledger_entry,
            "verification_metrics": verification_metrics,
        }

    def search_and_evaluate_all(
        self,
        destination: str,
        duration_hours: int = 2
    ) -> List[Dict[str, Any]]:
        """Processes decisions for all candidate lots near destination."""
        context = self.retrieval_agent.retrieve_context(destination, duration_hours=duration_hours)
        candidate_lots = context.get("candidate_lots", [])
        
        results = []
        for lot in candidate_lots:
            # Deterministic decision ID keyed to lot ID for stable navigation
            dec_id = f"dec-{lot['id']}"
            result = self.process_decision(lot["id"], duration_hours=duration_hours, decision_id=dec_id)
            results.append(result)
        return results
