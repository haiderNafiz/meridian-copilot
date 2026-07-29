from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..schema import FeedbackRecord, AuditRecord, PromotionRequest

class FeedbackProvider(ABC):
    @abstractmethod
    def save_feedback(self, record: FeedbackRecord) -> str:
        """Save feedback record to store."""
        pass

    @abstractmethod
    def get_feedback(self, feedback_id: str) -> Optional[FeedbackRecord]:
        """Retrieve feedback record from store."""
        pass

    @abstractmethod
    def list_feedback(self, filters: Dict[str, Any] = None) -> List[FeedbackRecord]:
        """Query and list feedback records matching filter settings."""
        pass

    @abstractmethod
    def save_audit(self, audit: AuditRecord) -> str:
        """Append log trace into audit trail."""
        pass

    @abstractmethod
    def list_audits(self, entity_id: str) -> List[AuditRecord]:
        """List audit traces for a specific target entity."""
        pass

    @abstractmethod
    def save_promotion(self, request: PromotionRequest) -> str:
        """Save promotion request."""
        pass

    @abstractmethod
    def get_promotion(self, promotion_id: str) -> Optional[PromotionRequest]:
        """Retrieve specific promotion request."""
        pass
