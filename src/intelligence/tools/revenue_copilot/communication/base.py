from abc import ABC, abstractmethod
from typing import Optional, List
from ..schema import DraftCommunication, FollowUpQuestion
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class CommunicationStrategy(ABC):
    @abstractmethod
    def generate(
        self, 
        assessment: OpportunityAssessment, 
        snapshot: ContextSnapshot
    ) -> Optional[DraftCommunication]:
        """Generate targeted communication drafts for the format (Email, CRM, etc.)."""
        pass

    def get_follow_ups(self, assessment: OpportunityAssessment) -> List[FollowUpQuestion]:
        """Identify missing context variables and build dialogue follow-ups."""
        return []
