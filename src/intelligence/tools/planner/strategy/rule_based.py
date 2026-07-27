from .base import PlannerStrategy
from ..schema import PlannerRequest, PlannerContext, PlannerConstraints, PlannerDecision
from ..catalog.base import WorkflowCatalog

class RuleBasedPlanner(PlannerStrategy):
    def plan(
        self,
        request: PlannerRequest,
        context: PlannerContext,
        catalog: WorkflowCatalog,
        constraints: PlannerConstraints
    ) -> PlannerDecision:
        query_lower = request.query_text.lower()
        
        # Enforce manual overrides first
        if request.force_workflow:
            template = catalog.get_template(request.force_workflow)
            if template:
                return PlannerDecision(
                    selected_workflow=request.force_workflow,
                    reasoning=f"Enforced workflow override specified: {request.force_workflow}",
                    confidence=1.0
                )
        
        # Rule 1: Candidate Assessment
        if any(kw in query_lower for kw in [
            "assess", "candidate", "resume", "profile", "qualification", "match",
            "years", "experience", "architect", "developer", "engineer", "cv", "is a"
        ]):
            return PlannerDecision(
                selected_workflow="CandidateAssessmentWorkflow",
                reasoning="Query indicates candidate evaluation or matching intent.",
                confidence=0.9
            )
            
        # Rule 2: Interview Prep
        if any(kw in query_lower for kw in ["interview", "prep", "preparation", "questions"]):
            return PlannerDecision(
                selected_workflow="InterviewWorkflow",
                reasoning="Query requests interview alignment or question generation.",
                confidence=0.95
            )
            
        # Rule 3: Memory/Knowledge Refresh
        if any(kw in query_lower for kw in ["history", "previous", "recall", "memory", "retrieve"]):
            return PlannerDecision(
                selected_workflow="ConversationWorkflow",
                reasoning="Query requests historical search or conversational snapshot recall.",
                confidence=0.85
            )

        # Default fallback: Recruiter Assistance
        return PlannerDecision(
            selected_workflow="RecruiterWorkflow",
            reasoning="Default general recruiter search workflow mapping.",
            confidence=0.7
        )
