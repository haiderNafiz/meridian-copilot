from .schema import RevenueCopilotRequest, RevenueCopilotResult
from .provider import RevenueCopilotProvider

class RevenueCopilotService:
    def __init__(self, provider: RevenueCopilotProvider):
        self.provider = provider

    def run(self, request: RevenueCopilotRequest) -> RevenueCopilotResult:
        """Process opportunity evaluation to compile action recommendations."""
        return self.provider.generate_recommendations(request)

_service_instance = None

def get_revenue_copilot_service() -> RevenueCopilotService:
    global _service_instance
    if _service_instance is None:
        from .playbook.default import DefaultPlaybookStrategy
        from .action.planner import ActionPlanner
        from .explanation.builder import ExplanationBuilder
        from .communication.email import EmailStrategy
        from .communication.crm import CRMStrategy
        from .communication.agenda import AgendaStrategy
        from .communication.proposal import ProposalStrategy
        
        playbook = DefaultPlaybookStrategy()
        planner = ActionPlanner()
        explanation = ExplanationBuilder()
        
        # Communication strategies registry
        comm_strategies = [
            EmailStrategy(),
            CRMStrategy(),
            AgendaStrategy(),
            ProposalStrategy()
        ]
        
        provider = RevenueCopilotProvider(
            playbook_strategy=playbook,
            action_planner=planner,
            comm_strategies=comm_strategies,
            explanation_builder=explanation
        )
        
        _service_instance = RevenueCopilotService(provider=provider)
    return _service_instance
