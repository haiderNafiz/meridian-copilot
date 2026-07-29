import datetime
from typing import Any, Dict, List, Optional
from .schema import FeedbackRecord, AuditRecord, FeedbackTarget, TargetType, FeedbackType
from .provider.base import FeedbackProvider
from .provider.file import LocalFilesystemFeedbackProvider
from .strategy import StrategyRegistry

class FeedbackService:
    def __init__(self, provider: Optional[FeedbackProvider] = None, strategy_registry: Optional[StrategyRegistry] = None):
        self.provider = provider or LocalFilesystemFeedbackProvider()
        self.strategy_registry = strategy_registry or StrategyRegistry()

    def submit_feedback(self, target_id: str, target_type: TargetType, run_id: str, feedback_type: FeedbackType, feedback_payload: Any, reviewer_id: Optional[str] = None, replay_id: Optional[str] = None, evaluation_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> FeedbackRecord:
        target = FeedbackTarget(target_id=target_id, target_type=target_type)
        
        strategy = self.strategy_registry.get_strategy(feedback_type)
        if strategy:
            if not strategy.validate(feedback_payload):
                raise ValueError(f"Invalid payload for feedback type {feedback_type}: {feedback_payload}")
            normalized_payload = strategy.normalize(feedback_payload)
        else:
            normalized_payload = feedback_payload

        record = FeedbackRecord(
            run_id=run_id,
            replay_id=replay_id,
            evaluation_id=evaluation_id,
            target=target,
            reviewer_id=reviewer_id,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
            feedback_type=feedback_type,
            feedback_payload=normalized_payload,
            metadata=metadata or {}
        )

        self.provider.save_feedback(record)

        audit = AuditRecord(
            entity_id=record.feedback_id,
            actor_id=reviewer_id or "system",
            action="create_feedback",
            timestamp=record.timestamp,
            changes={"feedback_type": feedback_type.value, "target_id": target_id}
        )
        self.provider.save_audit(audit)

        return record

    def get_feedback(self, feedback_id: str) -> Optional[FeedbackRecord]:
        return self.provider.get_feedback(feedback_id)

    def list_feedback(self, target_id: Optional[str] = None, run_id: Optional[str] = None) -> List[FeedbackRecord]:
        filters = {}
        if target_id:
            filters["target_id"] = target_id
        if run_id:
            filters["run_id"] = run_id
        return self.provider.list_feedback(filters=filters)

    def get_audits(self, entity_id: str) -> List[AuditRecord]:
        return self.provider.list_audits(entity_id)

_service_instance = None

def get_feedback_service() -> FeedbackService:
    global _service_instance
    if _service_instance is None:
        _service_instance = FeedbackService()
    return _service_instance
