from typing import Optional
from .base import CommunicationStrategy
from ..schema import DraftCommunication
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class ProposalStrategy(CommunicationStrategy):
    def generate(
        self, 
        assessment: OpportunityAssessment, 
        snapshot: ContextSnapshot
    ) -> Optional[DraftCommunication]:
        body = (
            f"PROPOSAL OUTLINE:\n"
            f"1. Executive Summary & Intent Alignment\n"
            f"2. Core Capabilities: {', '.join(getattr(snapshot.facts, 'normalized_technologies', []))}\n"
            f"3. Alignment Stage Target: {assessment.lifecycle_stage}\n"
            f"4. Action Directives Plan: {assessment.recommended_plan}"
        )
        return DraftCommunication(
            subject="Proposal Scope Draft",
            body=body,
            recipient_group="external"
        )
