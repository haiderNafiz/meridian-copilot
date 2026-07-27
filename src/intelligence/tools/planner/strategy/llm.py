from .base import PlannerStrategy
from ..schema import PlannerRequest, PlannerContext, PlannerConstraints, PlannerDecision
from ..catalog.base import WorkflowCatalog

class LLMPlanner(PlannerStrategy):
    def plan(
        self,
        request: PlannerRequest,
        context: PlannerContext,
        catalog: WorkflowCatalog,
        constraints: PlannerConstraints
    ) -> PlannerDecision:
        raise NotImplementedError("LLMPlanner is not implemented in Milestone 11.")
