from typing import Union
from .schema import PlannerRequest, PlannerResult, PlanningFailure, PlannerContext
from .provider import PlannerProvider

class PlannerService:
    def __init__(self, provider: PlannerProvider):
        self.provider = provider

    def plan(
        self,
        request: PlannerRequest,
        context_snapshot = None,
        retrieved_memories = None,
        available_tools = None
    ) -> Union[PlannerResult, PlanningFailure]:
        # Wrap context variables into structured models
        planner_ctx = PlannerContext(
            current_context=context_snapshot,
            retrieved_memories=retrieved_memories or [],
            available_tools=available_tools or []
        )
        return self.provider.generate_plan(request, planner_ctx)

_planner_service = None

def get_planner_service() -> PlannerService:
    global _planner_service
    if _planner_service is None:
        from .strategy.rule_based import RuleBasedPlanner
        from .catalog.base import WorkflowCatalog
        from .resolver.constraint import ConstraintResolver
        
        strategy = RuleBasedPlanner()
        catalog = WorkflowCatalog()
        resolver = ConstraintResolver()
        
        provider = PlannerProvider(strategy=strategy, catalog=catalog, constraint_resolver=resolver)
        _planner_service = PlannerService(provider=provider)
    return _planner_service
