from typing import Optional
from .base import CommunicationStrategy
from ..schema import DraftCommunication
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class AgendaStrategy(CommunicationStrategy):
    def generate(
        self, 
        assessment: OpportunityAssessment, 
        snapshot: ContextSnapshot
    ) -> Optional[DraftCommunication]:
        body = (
            f"AGENDA - NEXT TURN MEETING:\n"
            f"1. Discuss Matching Strengths: {', '.join(assessment.strengths[:2]) if assessment.strengths else 'None'}\n"
            f"2. Resolve Risks and Blockers: {', '.join(assessment.risks[:2]) if assessment.risks else 'None'}\n"
            f"3. Determine Custom Playbook Workflow Alignment: {assessment.recommended_plan}"
        )
        return DraftCommunication(
            subject="Meeting Agenda Draft",
            body=body,
            recipient_group="internal"
        )
