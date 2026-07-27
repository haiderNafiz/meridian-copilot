import uuid
import time
from typing import Union
from .schema import (
    PlannerRequest, PlannerContext, PlannerResult, 
    PlanningFailure, PlannerEvaluationMetrics
)
from .catalog.base import WorkflowCatalog, WorkflowTemplate
from .resolver.constraint import ConstraintResolver
from .strategy.base import PlannerStrategy
from src.intelligence.tools.agent_orchestrator.schema import ExecutionPlan

class PlannerProvider:
    def __init__(
        self,
        strategy: PlannerStrategy,
        catalog: WorkflowCatalog,
        constraint_resolver: ConstraintResolver
    ):
        self.strategy = strategy
        self.catalog = catalog
        self.constraint_resolver = constraint_resolver

    def generate_plan(
        self,
        request: PlannerRequest,
        context: PlannerContext
    ) -> Union[PlannerResult, PlanningFailure]:
        start_time = time.perf_counter()
        trace_id = f"pln_{uuid.uuid4().hex[:8]}"
        
        try:
            # 1. Strategy Workflow Classification
            constraints_stub = self.constraint_resolver.resolve_constraints(
                WorkflowTemplate(name="TempCheck", description="init", nodes=[]), context
            )
            decision = self.strategy.plan(request, context, self.catalog, constraints_stub)
            
            # 2. Retrieve Template Details
            template = self.catalog.get_template(decision.selected_workflow)
            if not template:
                return PlanningFailure(
                    error_code="WorkflowNotFound",
                    message=f"Workflow template '{decision.selected_workflow}' does not exist in catalog.",
                    trace_id=trace_id
                )
            
            # 3. Constraint Verification
            constraints = self.constraint_resolver.resolve_constraints(template, context)
            violations = self.constraint_resolver.validate(constraints)
            
            if violations:
                return PlanningFailure(
                    error_code="ConstraintViolation",
                    message="Failed to validate planning constraints for selected workflow.",
                    trace_id=trace_id,
                    missing_details=violations
                )
                
            # 4. Formulate ExecutionPlan Output
            execution_plan = ExecutionPlan(
                plan_id=str(uuid.uuid4()),
                nodes=template.nodes
            )
            
            latency = (time.perf_counter() - start_time) * 1000
            metrics = PlannerEvaluationMetrics(
                planning_latency_ms=latency,
                workflow_selection_confidence=decision.confidence,
                constraint_violations=violations,
                workflow_complexity=len(template.nodes),
                estimated_execution_cost=0.15 * len(template.nodes),
                estimated_execution_depth=len(template.nodes)
            )
            
            from src.intelligence.platform.metadata import ResponseMetadata
            res_metadata = ResponseMetadata(
                provider="rules",
                model="n/a",
                prompt_version="1.0.0",
                confidence=decision.confidence,
                fallback_used=False,
                provider_latency_ms=latency
            )
            return PlannerResult(
                status="success",
                metadata=res_metadata,
                execution_plan=execution_plan,
                planning_trace=trace_id,
                planner_reasoning_summary=decision.reasoning,
                confidence=decision.confidence,
                assumptions=decision.assumptions,
                missing_information=decision.missing_information,
                selected_workflow=decision.selected_workflow,
                metrics=metrics
            )
            
        except Exception as e:
            return PlanningFailure(
                error_code="InternalPlannerError",
                message=f"Planning execution encountered exception: {str(e)}",
                trace_id=trace_id
            )
