import functools
import datetime
import uuid
from typing import Any, Dict, Optional
from .schema import ReplayRecord
from .registry import ReplayRegistry
from ..evaluation_framework.hook.base import EvaluationHook
from ..evaluation_framework.schema import EvaluationItem, EvaluationRunResult

class ReplayCaptureHook(EvaluationHook):
    def __init__(self, registry: Optional[ReplayRegistry] = None):
        self.registry = registry or ReplayRegistry()

    def on_item_complete(self, item: EvaluationItem, result: EvaluationRunResult, context: Dict[str, Any]):
        run_id = context.get("run_id") or f"run_{uuid.uuid4().hex[:10]}"
        target_id = "evaluation_target"
        version = "latest"
        
        if context.get("config"):
            target_id = context["config"].target_id
            if context["config"].reproducibility:
                version = context["config"].reproducibility.model_version or "latest"
                
        record = ReplayRecord(
            run_id=run_id,
            target_id=target_id,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
            version=version,
            input_payload=item.input_payload,
            output_payload=result.actual_output,
            prompts=result.artifacts if result.artifacts else None,
            cost=result.cost.model_dump() if result.cost else None,
            resource=result.resource.model_dump() if result.resource else None
        )
        self.registry.register_replay(record)

def replay_capture(target_id: str, registry: Optional[ReplayRegistry] = None):
    """
    Decorator to automatically capture inputs and outputs of a target execution function.
    """
    reg = registry or ReplayRegistry()
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            input_payload = {}
            if args:
                input_payload["args"] = [str(a) for a in args]
            if kwargs:
                input_payload["kwargs"] = {k: v for k, v in kwargs.items() if k not in ("context", "job_context_data")}
                
            context = kwargs.get("context") or {}
            run_id = context.get("run_id") or context.get("job_id") or f"run_{uuid.uuid4().hex[:10]}"
            
            start_time = datetime.datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                output_payload = result
                error_msg = None
            except Exception as e:
                output_payload = {"error": str(e)}
                error_msg = str(e)
                raise e
            finally:
                end_time = datetime.datetime.utcnow()
                duration = (end_time - start_time).total_seconds() * 1000.0
                
                serializable_output = output_payload
                if hasattr(output_payload, "model_dump"):
                    serializable_output = output_payload.model_dump()
                elif hasattr(output_payload, "model_dump_json"):
                    try:
                        import json
                        serializable_output = json.loads(output_payload.model_dump_json())
                    except Exception:
                        pass
                        
                record = ReplayRecord(
                    run_id=run_id,
                    target_id=target_id,
                    timestamp=start_time.isoformat() + "Z",
                    version="latest",
                    input_payload=input_payload,
                    output_payload=serializable_output,
                    metadata={"error": error_msg} if error_msg else {},
                    resource={"duration_ms": duration}
                )
                reg.register_replay(record)
                
            return result
        return wrapper
    return decorator
