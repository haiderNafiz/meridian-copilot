import datetime
from typing import Any, Dict, List, Optional
from .schema import FeedbackRecord, FeedbackEvent

class FeedbackPipelineHook:
    def on_event(self, event: FeedbackEvent, context: Dict[str, Any]):
        """Triggered when a feedback event is dispatched in the pipeline."""
        pass

class FeedbackPipeline:
    def __init__(self, hooks: Optional[List[FeedbackPipelineHook]] = None):
        self.hooks = hooks or []

    def register_hook(self, hook: FeedbackPipelineHook):
        self.hooks.append(hook)

    def dispatch(self, record: FeedbackRecord, payload_snapshot: Any, context: Optional[Dict[str, Any]] = None) -> FeedbackEvent:
        event = FeedbackEvent(
            feedback_id=record.feedback_id,
            target=record.target,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
            payload_snapshot=payload_snapshot
        )
        
        run_context = context or {}
        for hook in self.hooks:
            try:
                hook.on_event(event, run_context)
            except Exception:
                pass
                
        return event
