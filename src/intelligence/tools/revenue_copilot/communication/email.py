from typing import Optional, List
from .base import CommunicationStrategy
from ..schema import DraftCommunication, FollowUpQuestion
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class EmailStrategy(CommunicationStrategy):
    def generate(
        self, 
        assessment: OpportunityAssessment, 
        snapshot: ContextSnapshot
    ) -> Optional[DraftCommunication]:
        subject = f"Next Steps regarding your profile: {getattr(snapshot.facts, 'role_type', 'Application')}"
        body = (
            f"Hello,\n\n"
            f"Thank you for connecting with us. We have processed your application and would like to proceed "
            f"with the next stage of our evaluation: {assessment.decision_guidance}.\n\n"
            f"Best regards,\nRevenue Operations"
        )
        return DraftCommunication(
            subject=subject,
            body=body,
            recipient_group="external"
        )

    def get_follow_ups(self, assessment: OpportunityAssessment) -> List[FollowUpQuestion]:
        follow_ups = []
        for item in assessment.follow_up_items:
            follow_ups.append(FollowUpQuestion(
                question=item,
                intent_target="general_clarification"
            ))
        return follow_ups
