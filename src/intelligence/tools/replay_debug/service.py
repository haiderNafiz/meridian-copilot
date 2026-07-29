from typing import Any, Dict, Optional, List
from .schema import ReplayRecord, ReplayExecutionResult, ReplayDiff, ReplayResponse
from .registry import ReplayRegistry
from .runner import ReplayRunner
from .analyzer import DifferenceAnalyzer
from .reporter import DebugReporter
from ..evaluation_framework.target import EvaluationTarget

class ReplayService:
    def __init__(
        self,
        registry: Optional[ReplayRegistry] = None,
        runner: Optional[ReplayRunner] = None,
        reporter: Optional[DebugReporter] = None
    ):
        self.registry = registry or ReplayRegistry()
        self.runner = runner or ReplayRunner()
        self.reporter = reporter or DebugReporter()

    def register_target(self, target_id: str, target: EvaluationTarget):
        self.runner.register_target(target_id, target)

    def create_replay(self, target_id: str, input_payload: Any, output_payload: Any, parent_replay_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> ReplayRecord:
        import datetime
        import uuid
        record = ReplayRecord(
            run_id=f"run_{uuid.uuid4().hex[:10]}",
            target_id=target_id,
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
            version="latest",
            input_payload=input_payload,
            output_payload=output_payload,
            parent_replay_id=parent_replay_id,
            metadata=metadata or {}
        )
        self.registry.register_replay(record)
        return record

    def replay_execution(self, replay_id: str, override_config: Optional[Dict[str, Any]] = None) -> ReplayExecutionResult:
        record = self.registry.get_replay(replay_id)
        if not record:
            raise FileNotFoundError(f"ReplayRecord {replay_id} not found")
        return self.runner.replay(record, override_config=override_config)

    def compare_replays(self, replay_id: str, override_config: Optional[Dict[str, Any]] = None) -> ReplayDiff:
        record = self.registry.get_replay(replay_id)
        if not record:
            raise FileNotFoundError(f"ReplayRecord {replay_id} not found")
        replayed = self.runner.replay(record, override_config=override_config)
        return DifferenceAnalyzer.analyze(record, replayed)

    def generate_debug_report(self, replay_id: str, override_config: Optional[Dict[str, Any]] = None, format: str = "json") -> str:
        record = self.registry.get_replay(replay_id)
        if not record:
            raise FileNotFoundError(f"ReplayRecord {replay_id} not found")
        replayed = self.runner.replay(record, override_config=override_config)
        diff = DifferenceAnalyzer.analyze(record, replayed)
        return self.reporter.generate_report(record, replayed, diff, format=format)

_service_instance = None

def get_replay_service() -> ReplayService:
    global _service_instance
    if _service_instance is None:
        _service_instance = ReplayService()
    return _service_instance
