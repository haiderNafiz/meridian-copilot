import uuid
from .base import PlanResolver
from ..schema import ExecutionPlan, ExecutionNode, OrchestrationRequest

class DefaultPlanResolver(PlanResolver):
    def resolve_plan(self, request: OrchestrationRequest) -> ExecutionPlan:
        if request.force_tools:
            nodes = []
            for t in request.force_tools:
                nodes.append(ExecutionNode(tool_name=t))
            return ExecutionPlan(plan_id=str(uuid.uuid4()), nodes=nodes)
            
        from src.intelligence.tools.planner.service import get_planner_service
        from src.intelligence.tools.planner.schema import PlannerRequest
        from src.intelligence.tools.agent_orchestrator.service import get_agent_orchestrator_service
        
        planner_req = PlannerRequest(
            query_text=request.query_text,
            session_id=request.session_id,
            context_id=request.context_id,
            email=request.email,
            location=request.location,
            technology_keywords=request.technology_keywords
        )
        
        # Get active tools for validation
        orchestrator = get_agent_orchestrator_service()
        tools = orchestrator.provider.registry.get_all_tools()
        
        result = get_planner_service().plan(
            request=planner_req,
            available_tools=tools
        )
        
        if result.status == "failure":
            raise ValueError(f"Planning failure [Code: {result.error_code}]: {result.message}. Details: {getattr(result, 'missing_details', [])}")
            
        return result.execution_plan
