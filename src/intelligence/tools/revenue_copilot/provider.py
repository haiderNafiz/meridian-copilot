import time
from typing import List
from .schema import RevenueCopilotRequest, RevenueCopilotResult, CopilotRecommendation
from .playbook.base import PlaybookStrategy
from .action.planner import ActionPlanner
from .communication.base import CommunicationStrategy
from .explanation.builder import ExplanationBuilder

class RevenueCopilotProvider:
    def __init__(
        self,
        playbook_strategy: PlaybookStrategy,
        action_planner: ActionPlanner,
        comm_strategies: List[CommunicationStrategy],
        explanation_builder: ExplanationBuilder
    ):
        self.playbook_strategy = playbook_strategy
        self.action_planner = action_planner
        self.comm_strategies = comm_strategies
        self.explanation_builder = explanation_builder

    def generate_recommendations(self, request: RevenueCopilotRequest) -> RevenueCopilotResult:
        start_time = time.perf_counter()
        
        # 1. Select playbook stage category and name
        playbook = self.playbook_strategy.select_playbook(request.opportunity_assessment)
        
        # 2. Plan actions into checklists
        checklist = self.action_planner.plan_actions(request.opportunity_assessment)
        
        # 3. Generate drafts and follow-ups via registry of strategies
        drafts = []
        follow_ups = []
        for strategy in self.comm_strategies:
            draft = strategy.generate(request.opportunity_assessment, request.context_snapshot)
            if draft:
                drafts.append(draft)
            follow_ups.extend(strategy.get_follow_ups(request.opportunity_assessment))
            
        # 4. Build explanation rationale
        explanation = self.explanation_builder.build_explanation(request.opportunity_assessment)
        
        rec = CopilotRecommendation(
            playbook=playbook,
            checklist=checklist,
            drafts=drafts,
            follow_up_questions=follow_ups,
            explanation=explanation
        )
        
        latency = (time.perf_counter() - start_time) * 1000
        
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus
        
        res_metadata = ResponseMetadata(
            provider="revenue_copilot_service",
            model="default_strategy",
            prompt_version="1.0.0",
            confidence=getattr(playbook, "confidence", 1.0),
            fallback_used=False,
            provider_latency_ms=latency
        )
        
        return RevenueCopilotResult(
            recommendation=rec,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
