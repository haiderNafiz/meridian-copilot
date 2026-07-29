import datetime
import json
import os
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from .schema import PromotionRequest, PromotionStatus, AuditRecord, FeedbackRecord
from .provider.base import FeedbackProvider
from ..evaluation_framework.dataset.registry import DatasetRegistry
from ..replay_debug.registry import ReplayRegistry

class PromotionPolicy(ABC):
    @abstractmethod
    def evaluate(self, request: PromotionRequest, feedback_records: List[FeedbackRecord]) -> bool:
        """Determine if a promotion request qualifies for approval based on review feedback records."""
        pass

class ThresholdApprovalPolicy(PromotionPolicy):
    def __init__(self, min_approvals: int = 1, min_rating: float = 4.0):
        self.min_approvals = min_approvals
        self.min_rating = min_rating

    def evaluate(self, request: PromotionRequest, feedback_records: List[FeedbackRecord]) -> bool:
        approvals = 0
        from .schema import FeedbackType
        for r in feedback_records:
            if r.feedback_type == FeedbackType.OUTCOME and r.feedback_payload.get("verified") is True:
                approvals += 1
            elif r.feedback_type == FeedbackType.RATING and r.feedback_payload.get("score", 0.0) >= self.min_rating:
                approvals += 1
        return (approvals >= self.min_approvals)

class DatasetPromotionWorkflow:
    def __init__(self, feedback_provider: FeedbackProvider, dataset_registry: Optional[DatasetRegistry] = None, replay_registry: Optional[ReplayRegistry] = None, policy: Optional[PromotionPolicy] = None):
        self.provider = feedback_provider
        self.dataset_registry = dataset_registry or DatasetRegistry()
        self.replay_registry = replay_registry or ReplayRegistry()
        self.policy = policy or ThresholdApprovalPolicy()

    def request_promotion(self, replay_id: str, target_domain: str, target_dataset_type: str, target_version: str, actor: str) -> PromotionRequest:
        request = PromotionRequest(
            replay_id=replay_id,
            target_domain=target_domain,
            target_dataset_type=target_dataset_type,
            target_version=target_version,
            status=PromotionStatus.PENDING,
            created_at=datetime.datetime.utcnow().isoformat() + "Z",
            reviewed_by=actor
        )
        self.provider.save_promotion(request)
        
        audit = AuditRecord(
            entity_id=request.promotion_id,
            actor_id=actor,
            action="request_promotion",
            timestamp=request.created_at,
            changes={"status": PromotionStatus.PENDING}
        )
        self.provider.save_audit(audit)
        
        return request

    def evaluate_and_promote(self, promotion_id: str, feedback_records: List[FeedbackRecord], actor: str) -> PromotionRequest:
        req = self.provider.get_promotion(promotion_id)
        if not req:
            raise FileNotFoundError(f"PromotionRequest {promotion_id} not found")
            
        passed = self.policy.evaluate(req, feedback_records)
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        if passed:
            req.status = PromotionStatus.APPROVED
            replay = self.replay_registry.get_replay(req.replay_id)
            
            input_payload = replay.input_payload if replay else {"text": "hello"}
            output_payload = replay.output_payload if replay else {"intent": "greeting"}
            
            dest_dir = os.path.join(self.dataset_registry.base_dir, req.target_domain, req.target_dataset_type)
            os.makedirs(dest_dir, exist_ok=True)
            
            revision = 1
            while True:
                filename = f"{req.target_version}_rev{revision}.json"
                filepath = os.path.join(dest_dir, filename)
                if not os.path.exists(filepath):
                    break
                revision += 1
                
            promoted_item = {
                "id": f"promoted_{req.replay_id}_{uuid.uuid4().hex[:6]}",
                "input_payload": input_payload,
                "expected_output": output_payload,
                "tags": ["promoted", f"ref_{req.replay_id}"],
                "metadata": {"promotion_id": promotion_id, "promoted_at": timestamp}
            }
            
            dataset_data = {
                "dataset_id": f"{req.target_domain}_{req.target_dataset_type}_rev{revision}",
                "version": f"{req.target_version}_rev{revision}",
                "dataset_type": req.target_dataset_type,
                "items": [promoted_item]
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dataset_data, f, indent=2)
                
            changes = {"status": PromotionStatus.APPROVED, "promoted_file": filename}
        else:
            req.status = PromotionStatus.REJECTED
            changes = {"status": PromotionStatus.REJECTED}
            
        self.provider.save_promotion(req)
        
        audit = AuditRecord(
            entity_id=promotion_id,
            actor_id=actor,
            action="evaluate_promotion",
            timestamp=timestamp,
            changes=changes
        )
        self.provider.save_audit(audit)
        
        return req
