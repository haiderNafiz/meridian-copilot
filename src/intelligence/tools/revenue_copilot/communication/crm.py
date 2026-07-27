from typing import Optional
from .base import CommunicationStrategy
from ..schema import DraftCommunication
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class CRMStrategy(CommunicationStrategy):
    def generate(
        self, 
        assessment: OpportunityAssessment, 
        snapshot: ContextSnapshot
    ) -> Optional[DraftCommunication]:
        body = (
            f"[CRM NOTE - AUTOMATED EVALUATION]\n"
            f"Opportunity Score: {assessment.opportunity_score}\n"
            f"Intent: {assessment.business_intent}\n"
            f"Strengths Match: {len(assessment.strengths)} items identified\n"
            f"Risks Flagged: {len(assessment.risks)} items identified\n"
            f"Guidance: {assessment.decision_guidance}"
        )
        return DraftCommunication(
            subject="CRM Activity Update",
            body=body,
            recipient_group="internal"
        )
