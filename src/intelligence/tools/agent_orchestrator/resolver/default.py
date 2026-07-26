import uuid
from .base import PlanResolver
from ..schema import ExecutionPlan, ExecutionNode, OrchestrationRequest

class DefaultPlanResolver(PlanResolver):
    def resolve_plan(self, request: OrchestrationRequest) -> ExecutionPlan:
        nodes = []
        if request.force_tools:
            for t in request.force_tools:
                nodes.append(ExecutionNode(tool_name=t))
        else:
            nodes.extend([
                ExecutionNode(
                    tool_name="intent_classifier",
                    arguments_mapping={"query_text": "initial_query"}
                ),
                ExecutionNode(
                    tool_name="candidate_profiler",
                    arguments_mapping={"raw_text": "initial_query"}
                ),
                ExecutionNode(
                    tool_name="deterministic_enricher",
                    arguments_mapping={
                        "email": "email",
                        "location": "location",
                        "technology_keywords": "technology_keywords",
                        "candidate_profile": "candidate_profiler"
                    }
                ),
                ExecutionNode(
                    tool_name="knowledge_service",
                    arguments_mapping={"query_text": "initial_query"}
                ),
                ExecutionNode(
                    tool_name="qualification_scorer",
                    arguments_mapping={
                        "candidate_profile": "candidate_profiler",
                        "candidate_enrichment": "deterministic_enricher",
                        "retrieved_context": "knowledge_service"
                    }
                ),
                ExecutionNode(
                    tool_name="summarizer",
                    arguments_mapping={
                        "candidate_profile": "candidate_profiler",
                        "candidate_enrichment": "deterministic_enricher",
                        "retrieved_context": "knowledge_service",
                        "qualification_scores": "qualification_scorer"
                    }
                ),
                ExecutionNode(
                    tool_name="context_builder",
                    arguments_mapping={
                        "context_id": "context_id",
                        "session_id": "session_id",
                        "raw_text": "initial_query",
                        "candidate_profile": "candidate_profiler",
                        "candidate_enrichment": "deterministic_enricher",
                        "retrieved_context": "knowledge_service",
                        "qualification_scores": "qualification_scorer",
                        "recruiter_summary": "summarizer"
                    }
                ),
                ExecutionNode(
                    tool_name="save_memory",
                    arguments_mapping={
                        "snapshot": "context_builder.payload",
                        "session_id": "session_id"
                    }
                )
            ])
        return ExecutionPlan(plan_id=str(uuid.uuid4()), nodes=nodes)
