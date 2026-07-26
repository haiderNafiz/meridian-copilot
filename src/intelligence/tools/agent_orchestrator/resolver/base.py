from abc import ABC, abstractmethod
from ..schema import ExecutionPlan, OrchestrationRequest

class PlanResolver(ABC):
    @abstractmethod
    def resolve_plan(self, request: OrchestrationRequest) -> ExecutionPlan:
        """Resolve an execution plan based on request inputs."""
        pass
