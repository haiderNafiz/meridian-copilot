from abc import ABC, abstractmethod
from typing import Any, Dict
import time
from .schema import ExecutionResult, ResourceMetrics, CostMetrics

class EvaluationTarget(ABC):
    @abstractmethod
    def execute(self, input_payload: Dict[str, Any], context: Dict[str, Any]) -> ExecutionResult:
        """Execute the target (tool, pipeline, agent) and return results."""
        pass

class ToolTarget(EvaluationTarget):
    def __init__(self, tool_name: str, executor: Any = None):
        self.tool_name = tool_name
        self.executor = executor  # Mapped function or executor class

    def execute(self, input_payload: Dict[str, Any], context: Dict[str, Any]) -> ExecutionResult:
        start_time = time.perf_counter()
        
        # Invoke mock or execute tool
        if self.executor:
            actual_output = self.executor(input_payload)
        else:
            actual_output = {"result": "mocked", "tool": self.tool_name, "input": input_payload}
            
        latency = (time.perf_counter() - start_time) * 1000
        
        # Populate basic utilization metrics
        resource = ResourceMetrics(
            cpu_percent=1.5,
            peak_ram_mb=120.0,
            average_ram_mb=115.0,
            duration_ms=latency,
            throughput_items_per_sec=1000.0 / (latency if latency > 0 else 1.0)
        )
        
        # Populate basic cost metrics
        cost = CostMetrics(
            prompt_tokens=50,
            completion_tokens=10,
            estimated_cost=0.001,
            currency="USD",
            provider="mock"
        )
        
        return ExecutionResult(
            actual_output=actual_output,
            latency_ms=latency,
            cost=cost,
            resource=resource,
            artifacts={"prompt": f"Mock prompt for {self.tool_name}"}
        )

class WorkflowTarget(EvaluationTarget):
    def execute(self, input_payload: Dict[str, Any], context: Dict[str, Any]) -> ExecutionResult:
        # Placeholder E2E workflow target execution
        res = ToolTarget("workflow").execute(input_payload, context)
        return res
