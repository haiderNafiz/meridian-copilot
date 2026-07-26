from src.intelligence.platform.contracts import ResponseStatus
from src.intelligence.platform.metadata import ResponseMetadata
from .schema import OrchestrationRequest, OrchestrationResult
from .policy.retry import RetryPolicy
from .policy.failure import FailurePolicy

class AgentOrchestratorService:
    def __init__(self, provider, retry_policy: RetryPolicy, failure_policy: FailurePolicy):
        self.provider = provider
        self.retry_policy = retry_policy
        self.failure_policy = failure_policy

    def process(self, request: OrchestrationRequest) -> OrchestrationResult:
        # 1. Generate plan
        plan = self.provider.generate_plan(request)
        
        # 2. Run tools loop
        context = self.provider.execute_plan(
            plan=plan,
            request=request,
            retry_policy=self.retry_policy,
            failure_policy=self.failure_policy
        )
        
        # 3. Extract ContextSnapshot
        context_snapshot = None
        if "context_builder" in context.outputs:
            builder_res = context.outputs["context_builder"]
            if hasattr(builder_res, "payload"):
                context_snapshot = builder_res.payload
            elif hasattr(builder_res, "context_snapshot"):
                context_snapshot = builder_res.context_snapshot
            elif isinstance(builder_res, dict):
                context_snapshot = builder_res.get("payload") or builder_res.get("context_snapshot")
                
        completed_steps = [k for k, v in context.outputs.items() if not (isinstance(v, dict) and v.get("failed"))]
        failed_steps = [k for k, v in context.outputs.items() if (isinstance(v, dict) and v.get("failed"))]
        
        metadata = ResponseMetadata(
            provider="agent_orchestrator",
            model="n/a",
            prompt_version="n/a",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        return OrchestrationResult(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            context_snapshot=context_snapshot,
            execution_trace_id=context.trace_id,
            completed_steps=completed_steps,
            failed_steps=failed_steps
        )

_agent_orchestrator_service = None

def get_agent_orchestrator_service() -> AgentOrchestratorService:
    global _agent_orchestrator_service
    if _agent_orchestrator_service is None:
        import uuid
        from .registry.simple import SimpleToolRegistry
        from .executor.direct import DirectToolExecutor
        from .resolver.default import DefaultPlanResolver
        from .schema import ToolMetadata
        from .policy.retry import RetryPolicy
        from .policy.failure import FailurePolicy
        from .provider import AgentOrchestratorProvider
        
        from src.intelligence.tools.intent_classifier.classifier import IntentClassifier
        from src.intelligence.tools.candidate_profiler.profiler import get_candidate_profiler_service
        from src.intelligence.tools.deterministic_enricher.service import DeterministicEnrichmentService
        from src.intelligence.tools.knowledge_service.service import RetrievalService
        from src.intelligence.tools.knowledge_service.provider import RetrievalProvider
        from src.intelligence.tools.knowledge_service.store.mock_store import MockVectorStore
        from src.intelligence.tools.knowledge_service.embedding.mock_embed import MockEmbeddingProvider
        from src.intelligence.tools.knowledge_service.ranking.cosine import CosineSimilarityRanker
        from src.intelligence.tools.qualification_scorer.service import get_qualification_scorer_service
        from src.intelligence.tools.summarizer.service import get_summarization_service
        from src.intelligence.tools.context_builder.service import get_context_builder_service
        from src.intelligence.tools.memory_service.service import get_memory_service
        
        registry = SimpleToolRegistry()
        executor = DirectToolExecutor()
        resolver = DefaultPlanResolver()
        
        # 1. Intent Classifier
        registry.register_tool(
            ToolMetadata(name="intent_classifier"),
            lambda query_text: IntentClassifier().classify(query_text)
        )
        
        # 2. Candidate Profiler
        from src.intelligence.tools.candidate_profiler.schema import CandidateInput
        registry.register_tool(
            ToolMetadata(name="candidate_profiler"),
            lambda raw_text: get_candidate_profiler_service().profile(CandidateInput(raw_text=raw_text))[0]
        )
        
        # 3. Deterministic Enricher
        from src.intelligence.tools.deterministic_enricher.schema import EnrichmentInput
        registry.register_tool(
            ToolMetadata(name="deterministic_enricher", dependencies=["candidate_profiler"]),
            lambda email, location, technology_keywords, candidate_profile: DeterministicEnrichmentService().process(
                EnrichmentInput(
                    email=email,
                    location=location,
                    technology_keywords=technology_keywords or (candidate_profile.technical_domains if candidate_profile else [])
                )
            )
        )
        
        # 4. Knowledge Service
        from src.intelligence.tools.knowledge_service.schema import RetrievalInput
        knowledge_impl = RetrievalService(
            provider=RetrievalProvider(
                store=MockVectorStore(),
                embedding=MockEmbeddingProvider(),
                ranker=CosineSimilarityRanker()
            )
        )
        registry.register_tool(
            ToolMetadata(name="knowledge_service"),
            lambda query_text: knowledge_impl.process(RetrievalInput(query=query_text))
        )
        
        # 5. Qualification Scorer
        from src.intelligence.tools.qualification_scorer.schema import QualificationOutput
        registry.register_tool(
            ToolMetadata(name="qualification_scorer", dependencies=["candidate_profiler", "deterministic_enricher", "knowledge_service"]),
            lambda candidate_profile, candidate_enrichment, retrieved_context: QualificationOutput(
                status=ResponseStatus.SUCCESS,
                metadata=ResponseMetadata(
                    provider="groq",
                    model=get_qualification_scorer_service().scorer_provider.model,
                    prompt_version=get_qualification_scorer_service().scorer_provider.prompt_version,
                    confidence=1.0,
                    fallback_used=False,
                    provider_latency_ms=0.0
                ),
                payload=get_qualification_scorer_service().scorer_provider.infer(
                    profile=candidate_profile,
                    enrichment=candidate_enrichment,
                    retrieval=retrieved_context.payload
                )[0]
            )
        )
        
        # 6. Summarizer
        import json
        from src.intelligence.tools.summarizer.schema import SummarizationOutput, SummaryType
        registry.register_tool(
            ToolMetadata(
                name="summarizer", 
                dependencies=["candidate_profiler", "deterministic_enricher", "knowledge_service", "qualification_scorer"]
            ),
            lambda candidate_profile, candidate_enrichment, retrieved_context, qualification_scores: SummarizationOutput(
                status=ResponseStatus.SUCCESS,
                metadata=ResponseMetadata(
                    provider="groq",
                    model=get_summarization_service().summarizer_provider.model,
                    prompt_version="1.0.0",
                    confidence=1.0,
                    fallback_used=False,
                    provider_latency_ms=0.0
                ),
                payload=get_summarization_service().summarizer_provider.infer(
                    SummaryType.CANDIDATE,
                    json.dumps({
                        "candidate_profile": candidate_profile.model_dump() if candidate_profile else {},
                        "candidate_enrichment": candidate_enrichment.payload.model_dump() if candidate_enrichment else {},
                        "retrieved_context": [c.model_dump() for c in retrieved_context.payload.results] if (retrieved_context and retrieved_context.payload) else [],
                        "qualification_scores": qualification_scores.payload.model_dump()
                    }, indent=2)
                )[0]
            )
        )
        
        # 7. Context Builder
        from src.intelligence.tools.context_builder.schema import ContextBuilderInput
        registry.register_tool(
            ToolMetadata(
                name="context_builder", 
                dependencies=[
                    "candidate_profiler", "deterministic_enricher", "knowledge_service", 
                    "qualification_scorer", "summarizer"
                ]
            ),
            lambda context_id, session_id, raw_text, candidate_profile, candidate_enrichment, retrieved_context, qualification_scores, recruiter_summary: get_context_builder_service().process(
                ContextBuilderInput(
                    context_id=context_id or str(uuid.uuid4()),
                    session_id=session_id,
                    document_references=[],
                    raw_text=raw_text,
                    candidate_profile=candidate_profile,
                    candidate_enrichment=candidate_enrichment,
                    retrieved_context=retrieved_context.payload.results if (retrieved_context and hasattr(retrieved_context, "payload") and retrieved_context.payload) else [],
                    qualification_scores=qualification_scores.payload if (qualification_scores and hasattr(qualification_scores, "payload")) else None,
                    recruiter_summary=recruiter_summary.payload if (recruiter_summary and hasattr(recruiter_summary, "payload")) else None
                )
            )
        )
        
        # 8. Memory Service save_memory
        from src.intelligence.tools.memory_service.schema import MemoryStoreRequest
        registry.register_tool(
            ToolMetadata(name="save_memory", dependencies=["context_builder"]),
            lambda snapshot, session_id: get_memory_service().save_memory(
                MemoryStoreRequest(
                    snapshot=snapshot,
                    session_id=session_id,
                    tags=snapshot.facts.technical_domains + snapshot.facts.normalized_technologies,
                    importance=0.8
                )
            )
        )
        
        provider = AgentOrchestratorProvider(registry=registry, executor=executor, resolver=resolver)
        retry_policy = RetryPolicy()
        failure_policy = FailurePolicy()
        
        _agent_orchestrator_service = AgentOrchestratorService(
            provider=provider,
            retry_policy=retry_policy,
            failure_policy=failure_policy
        )
    return _agent_orchestrator_service
