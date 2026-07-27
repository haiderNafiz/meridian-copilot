from typing import List
from ..schema import PlannerContext, PlannerConstraints
from ..catalog.base import WorkflowTemplate

class ConstraintResolver:
    def resolve_constraints(
        self,
        template: WorkflowTemplate,
        context: PlannerContext
    ) -> PlannerConstraints:
        # Check active tool registrations
        registered_tools = {t.name for t in context.available_tools}
        disabled_tools = {t.name for t in context.available_tools if not t.enabled}
        
        required_tools = [node.tool_name for node in template.nodes]
        
        # Track context specifications
        context_requirements = []
        if template.name == "CandidateAssessmentWorkflow":
            context_requirements.extend(["session_id"])
            
        return PlannerConstraints(
            required_tools=required_tools,
            available_tools=list(registered_tools),
            disabled_tools=list(disabled_tools),
            context_requirements=context_requirements,
            memory_availability=True
        )

    def validate(self, constraints: PlannerConstraints) -> List[str]:
        violations = []
        for tool in constraints.required_tools:
            if tool not in constraints.available_tools:
                violations.append(f"ToolNotFound: Required tool '{tool}' is not registered in System Registry.")
            elif tool in constraints.disabled_tools:
                violations.append(f"ToolDisabled: Required tool '{tool}' is currently deactivated.")
        return violations
