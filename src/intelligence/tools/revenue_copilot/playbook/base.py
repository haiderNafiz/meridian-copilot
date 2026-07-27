from abc import ABC, abstractmethod
from ..schema import PlaybookRecommendation
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment

class PlaybookStrategy(ABC):
    @abstractmethod
    def select_playbook(self, assessment: OpportunityAssessment) -> PlaybookRecommendation:
        """Analyze assessment and select the matching playbook category and name."""
        pass
