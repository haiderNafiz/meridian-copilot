from abc import ABC, abstractmethod
from ..schema import OpportunityAssessment
from src.intelligence.tools.context_builder.schema import ContextSnapshot
from src.intelligence.tools.conversation_memory.schema import ConversationContext

class OpportunityAssessmentStrategy(ABC):
    @abstractmethod
    def assess(
        self,
        snapshot: ContextSnapshot,
        conv_context: ConversationContext,
        evidence_summary: dict
    ) -> OpportunityAssessment:
        """Evaluate snapshot data and assemble a structured assessment."""
        pass
