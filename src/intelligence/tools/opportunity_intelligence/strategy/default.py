from ..schema import OpportunityAssessment, AssessmentType
from .base import OpportunityAssessmentStrategy
from src.intelligence.tools.context_builder.schema import ContextSnapshot
from src.intelligence.tools.conversation_memory.schema import ConversationContext

class DefaultAssessmentStrategy(OpportunityAssessmentStrategy):
    def assess(
        self,
        snapshot: ContextSnapshot,
        conv_context: ConversationContext,
        evidence_summary: dict
    ) -> OpportunityAssessment:
        # Determine opportunity score from overall qualification if present
        overall_score = 0.5
        qual_payload = snapshot.outputs.qualification_scores if snapshot.outputs else None
        if qual_payload:
            scores = getattr(qual_payload, "scores", {})
            overall_obj = scores.get("overall_qualification")
            if overall_obj:
                overall_score = getattr(overall_obj, "score", 0.5)

        # Extract business intent statement
        business_intent = "Assess candidate application suitability"
        if snapshot.inputs and snapshot.inputs.raw_text:
            business_intent = f"Assess intent from query: {snapshot.inputs.raw_text}"

        # Resolve recommended plan/playbook
        recommended_plan = "candidate_screening"
        if overall_score >= 0.8:
            recommended_plan = "technical_interview"
        elif overall_score < 0.3:
            recommended_plan = "client_followup"

        # Construct decision guidance
        guidance = "Proceed with standard phone screening."
        if overall_score >= 0.7:
            guidance = "Recommended to fast-track to hiring manager review."
        elif overall_score < 0.4:
            guidance = "Recommend reject or hold due to low compatibility score."

        # Extract follow-up items
        follow_up = []
        if conv_context and conv_context.unresolved_questions:
            follow_up = conv_context.unresolved_questions

        return OpportunityAssessment(
            assessment_type=AssessmentType.CANDIDATE,
            business_intent=business_intent,
            lifecycle_stage="Vetting",
            confidence=evidence_summary.get("evidence_completeness", 0.8),
            opportunity_score=overall_score,
            strengths=evidence_summary.get("strengths", []),
            risks=evidence_summary.get("risks", []),
            blockers=evidence_summary.get("blockers", []),
            missing_information=evidence_summary.get("missing_information", []),
            evidence_summary=evidence_summary,
            recommended_next_actions=evidence_summary.get("recommended_next_actions", []),
            recommended_plan=recommended_plan,
            follow_up_items=follow_up,
            decision_guidance=guidance,
            explanation=f"Default opportunity assessment completed with overall matching score {overall_score}.",
            telemetry={"telemetry_version": "1.0.0"}
        )
