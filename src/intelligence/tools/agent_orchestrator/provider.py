import uuid
from .schema import ExecutionPlan, ExecutionContext, OrchestrationRequest
from .registry.base import ToolRegistry
from .resolver.base import PlanResolver
from .executor.base import ToolExecutor

class AgentOrchestratorProvider:
    def __init__(self, registry: ToolRegistry, executor: ToolExecutor, resolver: PlanResolver):
        self.registry = registry
        self.executor = executor
        self.resolver = resolver

    def generate_plan(self, request: OrchestrationRequest) -> ExecutionPlan:
        return self.resolver.resolve_plan(request)

    def execute_plan(
        self, 
        plan: ExecutionPlan, 
        request: OrchestrationRequest,
        retry_policy,
        failure_policy
    ) -> ExecutionContext:
        context = ExecutionContext(
            trace_id=f"tr_orch_{uuid.uuid4().hex[:8]}",
            session_id=request.session_id,
            outputs={
                "initial_query": request.query_text,
                "email": request.email,
                "location": request.location,
                "technology_keywords": request.technology_keywords
            }
        )
        
        if request.context_id:
            context.outputs["context_id"] = request.context_id
        if request.session_id:
            context.outputs["session_id"] = request.session_id
            
        for node in plan.nodes:
            metadata = self.registry.get_metadata(node.tool_name)
            func = self.registry.get_tool(node.tool_name)
            
            if not metadata or not func or not metadata.enabled:
                continue
                
            try:
                result = self.executor.execute(
                    node=node,
                    metadata=metadata,
                    func=func,
                    context=context,
                    retry_policy=retry_policy,
                    failure_policy=failure_policy
                )
                context.outputs[node.tool_name] = result
            except Exception as e:
                if failure_policy.should_abort():
                    raise e
                context.outputs[node.tool_name] = {"error": str(e), "failed": True}
                
        return context
