from abc import ABC, abstractmethod
from ..schema import PlannerRequest, PlannerContext, PlannerConstraints, PlannerDecision
from ..catalog.base import WorkflowCatalog

class PlannerStrategy(ABC):
    @abstractmethod
    def plan(
        self,
        request: PlannerRequest,
        context: PlannerContext,
        catalog: WorkflowCatalog,
        constraints: PlannerConstraints
    ) -> PlannerDecision:
        """Resolve a selected workflow and reasoning mapping from requests and context."""
        pass
