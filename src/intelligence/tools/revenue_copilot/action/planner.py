from ..schema import ActionChecklist
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment

class ActionPlanner:
    def plan_actions(self, assessment: OpportunityAssessment) -> ActionChecklist:
        critical = []
        required = []
        advisory = []
        
        # Map blocker signals to critical
        for blocker in assessment.blockers:
            critical.append(f"Blocker resolution: {blocker}")
            
        # Map missing_information to required
        for item in assessment.missing_information:
            required.append(f"Request missing attribute: {item}")
            
        # Map risks to advisory
        for risk in assessment.risks:
            advisory.append(f"Mitigate flagged risk: {risk}")
            
        # Prioritize next steps
        for action in assessment.recommended_next_actions:
            if "CRITICAL" in action:
                critical.append(action)
            elif "REQUIRED" in action:
                required.append(action)
            else:
                advisory.append(action)
                
        return ActionChecklist(
            critical_actions=critical,
            required_actions=required,
            advisory_actions=advisory
        )
