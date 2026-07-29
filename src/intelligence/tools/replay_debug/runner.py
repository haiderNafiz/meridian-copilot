import datetime
from typing import Any, Dict, Optional
from .schema import ReplayRecord, ReplayExecutionResult
from ..evaluation_framework.target import EvaluationTarget, ToolTarget

class ReplayRunner:
    def __init__(self):
        self.targets: Dict[str, EvaluationTarget] = {}

    def register_target(self, target_id: str, target: EvaluationTarget):
        self.targets[target_id] = target

    def replay(self, record: ReplayRecord, override_config: Optional[Dict[str, Any]] = None) -> ReplayExecutionResult:
        target_id = record.target_id
        
        if target_id in self.targets:
            target = self.targets[target_id]
        else:
            target = ToolTarget(tool_name=target_id)
            
        context = {
            "run_id": record.run_id,
            "override_config": override_config or {}
        }
        
        exec_payload = record.input_payload
        if isinstance(exec_payload, dict) and "kwargs" in exec_payload:
            exec_payload = exec_payload["kwargs"]
            
        start_time = datetime.datetime.utcnow()
        exec_res = target.execute(exec_payload, context)
        end_time = datetime.datetime.utcnow()
        
        repro_dict = {
            "model_version": override_config.get("model_version") if override_config else "latest",
            "provider": override_config.get("provider") if override_config else "mock"
        }
        
        return ReplayExecutionResult(
            replay_id=record.replay_id,
            replayed_at=end_time.isoformat() + "Z",
            output_payload=exec_res.actual_output,
            cost=exec_res.cost.model_dump() if exec_res.cost else None,
            resource=exec_res.resource.model_dump() if exec_res.resource else None,
            config_overridden=override_config is not None and len(override_config) > 0,
            reproducibility=repro_dict
        )
