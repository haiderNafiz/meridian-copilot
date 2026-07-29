import os
import json
from typing import Any, Dict, List, Optional
from .base import FeedbackProvider
from ..schema import FeedbackRecord, AuditRecord, PromotionRequest

class LocalFilesystemFeedbackProvider(FeedbackProvider):
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../../feedback")
            )
        else:
            self.base_dir = os.path.abspath(base_dir)
            
        self.feedback_dir = os.path.join(self.base_dir, "records")
        self.audit_dir = os.path.join(self.base_dir, "audits")
        self.promotion_dir = os.path.join(self.base_dir, "promotions")
        
        os.makedirs(self.feedback_dir, exist_ok=True)
        os.makedirs(self.audit_dir, exist_ok=True)
        os.makedirs(self.promotion_dir, exist_ok=True)

    def save_feedback(self, record: FeedbackRecord) -> str:
        filepath = os.path.join(self.feedback_dir, f"{record.feedback_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(record.model_dump_json(indent=2))
        return filepath

    def get_feedback(self, feedback_id: str) -> Optional[FeedbackRecord]:
        filepath = os.path.join(self.feedback_dir, f"{feedback_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return FeedbackRecord.model_validate(data)

    def list_feedback(self, filters: Dict[str, Any] = None) -> List[FeedbackRecord]:
        results = []
        if not os.path.exists(self.feedback_dir):
            return results
            
        for filename in os.listdir(self.feedback_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.feedback_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        record = FeedbackRecord.model_validate(data)
                        
                        match = True
                        if filters:
                            for key, val in filters.items():
                                if key == "target_id":
                                    if record.target.target_id != val:
                                        match = False
                                        break
                                else:
                                    if getattr(record, key, None) != val:
                                        match = False
                                        break
                        if match:
                            results.append(record)
                except Exception:
                    continue
        return results

    def save_audit(self, audit: AuditRecord) -> str:
        filepath = os.path.join(self.audit_dir, f"{audit.audit_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(audit.model_dump_json(indent=2))
        return filepath

    def list_audits(self, entity_id: str) -> List[AuditRecord]:
        results = []
        if not os.path.exists(self.audit_dir):
            return results
            
        for filename in os.listdir(self.audit_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.audit_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        audit = AuditRecord.model_validate(data)
                        if audit.entity_id == entity_id:
                            results.append(audit)
                except Exception:
                    continue
        return results

    def save_promotion(self, request: PromotionRequest) -> str:
        filepath = os.path.join(self.promotion_dir, f"{request.promotion_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(request.model_dump_json(indent=2))
        return filepath

    def get_promotion(self, promotion_id: str) -> Optional[PromotionRequest]:
        filepath = os.path.join(self.promotion_dir, f"{promotion_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return PromotionRequest.model_validate(data)
