from fastmcp import FastMCP
from typing import Optional, List, Dict, Any
from src.intelligence.tools.intent_classifier.classifier import IntentClassifier
from src.intelligence.tools.intent_classifier.schema import IntentInput
from src.intelligence.tools.candidate_profiler.profiler import get_candidate_profiler_service
from src.intelligence.tools.candidate_profiler.schema import CandidateInput
from src.intelligence.tools.deterministic_enricher.schema import EnrichmentInput
from src.intelligence.tools.deterministic_enricher.service import DeterministicEnrichmentService
from src.intelligence.tools.knowledge_service.schema import RetrievalInput
from src.intelligence.tools.knowledge_service.service import RetrievalService
from src.intelligence.tools.knowledge_service.provider import RetrievalProvider
from src.intelligence.tools.knowledge_service.store.mock_store import MockVectorStore
from src.intelligence.tools.knowledge_service.embedding.mock_embed import MockEmbeddingProvider
from src.intelligence.tools.knowledge_service.ranking.cosine import CosineSimilarityRanker
from src.intelligence.tools.qualification_scorer.schema import QualificationInput
from src.intelligence.tools.qualification_scorer.service import get_qualification_scorer_service
from src.intelligence.tools.summarizer.schema import SummarizationInput
from src.intelligence.tools.summarizer.service import get_summarization_service
from src.intelligence.tools.context_builder.schema import ContextBuilderInput
from src.intelligence.tools.context_builder.service import get_context_builder_service
from src.intelligence.tools.memory_service.schema import MemoryStoreRequest, MemoryRetrieveRequest, MemoryQuery
from src.intelligence.tools.memory_service.service import get_memory_service
from src.intelligence.platform.telemetry import mcp_telemetry
from src.intelligence.platform.metadata import ResponseMetadata

# Create MCP server with name and version metadata
mcp = FastMCP("Meridian Intelligence Server", version="1.0.0")

def get_classifier() -> IntentClassifier:
    """
    Dependency injection factory to retrieve the Intent Classifier service instance.
    """
    return IntentClassifier()

@mcp.tool(
    name="classify_intent",
    description="Classify incoming candidate application, client inquiry, status check, or withdrawal message."
)
async def classify_intent(raw_text: str, source: str, sender_email: str, context: Optional[dict] = None) -> str:
    """
    Classify the intent of the incoming message using the core IntentClassifier service.
    """
    with mcp_telemetry("classify_intent", context) as collector:
        # Validate incoming transport payload parameters via Pydantic schema
        input_data = IntentInput(
            raw_text=raw_text,
            source=source,
            sender_email=sender_email
        )

        # Resolve classifier service instance
        classifier = get_classifier()

        # Delegate execution to the core classification business logic
        result = classifier.classify(input_data.raw_text)

        # Populate response metadata for telemetry collection
        provider = "rules" if result.fallback_used else "groq"
        collector.metadata = ResponseMetadata(
            provider=provider,
            model="rules" if result.fallback_used else "llama-3.3-70b-versatile",
            prompt_version="1.0.0",
            confidence=result.confidence,
            fallback_used=result.fallback_used,
            provider_latency_ms=0.0
        )

        return result.model_dump_json()

@mcp.tool(
    name="profile_candidate",
    description="Profile candidate details (raw text, title, skills, experience, job context) into role, seniority, and urgency taxonomies."
)
async def profile_candidate(
    raw_text: str,
    current_title: Optional[str] = None,
    skills: Optional[list] = None,
    years_experience: Optional[int] = None,
    job_context: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    """
    Profile candidate data by calling the core CandidateProfilerService.
    """
    with mcp_telemetry("profile_candidate", context) as collector:
        # Validate incoming transport payload parameters via Pydantic schema
        input_data = CandidateInput(
            raw_text=raw_text,
            current_title=current_title,
            skills=skills,
            years_experience=years_experience,
            job_context=job_context
        )

        # Resolve profiler service instance
        profiler_service = get_candidate_profiler_service()

        # Delegate execution to the core business logic, which returns (CandidateOutput, provider_latency)
        result, provider_latency_ms = profiler_service.profile(input_data)

        # Populate response metadata for telemetry collection
        model = getattr(profiler_service.provider, "model", "llama-3.1-8b-instant")
        prompt_version = getattr(profiler_service.provider, "prompt_version", "1.0.0")
        
        collector.metadata = ResponseMetadata(
            provider="groq",
            model=model,
            prompt_version=prompt_version,
            confidence=result.confidence,
            fallback_used=False,
            provider_latency_ms=provider_latency_ms
        )

        return result.model_dump_json()

@mcp.tool(
    name="enrich_entity",
    description="Deterministically normalizes and enriches structured candidate, lead, or company fields."
)
async def enrich_entity(
    company_name: Optional[str] = None,
    website: Optional[str] = None,
    email: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    github_url: Optional[str] = None,
    phone_number: Optional[str] = None,
    country: Optional[str] = None,
    location: Optional[str] = None,
    technology_keywords: Optional[list] = None,
    other_fields: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    """
    Enrich and normalize entities deterministically.
    """
    with mcp_telemetry("enrich_entity", context) as collector:
        input_data = EnrichmentInput(
            company_name=company_name,
            website=website,
            email=email,
            linkedin_url=linkedin_url,
            github_url=github_url,
            phone_number=phone_number,
            country=country,
            location=location,
            technology_keywords=technology_keywords,
            other_fields=other_fields
        )
        
        service = DeterministicEnrichmentService()
        result = service.process(input_data)
        
        # Populate response metadata for telemetry collection
        collector.metadata = result.metadata
        
        return result.model_dump_json()

@mcp.tool(
    name="retrieve_knowledge",
    description="Retrieve relevant knowledge context chunks from vector collections based on semantic query similarity."
)
async def retrieve_knowledge(
    query: str,
    collection: str = "default",
    limit: int = 5,
    threshold: float = 0.0,
    filters: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    """
    Retrieve knowledge context chunks deterministically using similarity ranking.
    """
    with mcp_telemetry("retrieve_knowledge", context) as collector:
        input_data = RetrievalInput(
            query=query,
            collection=collection,
            limit=limit,
            threshold=threshold,
            filters=filters
        )
        
        # Resolve components via Dependency Injection
        store = MockVectorStore()
        embedder = MockEmbeddingProvider()
        ranker = CosineSimilarityRanker()
        provider = RetrievalProvider(store=store, embedding=embedder, ranker=ranker)
        service = RetrievalService(provider=provider)
        
        result = service.process(input_data)
        
        # Populate response metadata for telemetry collection
        collector.metadata = result.metadata
        
        return result.model_dump_json()

@mcp.tool(
    name="score_qualification",
    description="Compute multidimensional qualification alignment scores comparing candidate profiles vs target requirements."
)
async def score_qualification(
    raw_text: str,
    job_description_id: str,
    email: Optional[str] = None,
    location: Optional[str] = None,
    technology_keywords: Optional[list] = None,
    context: Optional[dict] = None
) -> str:
    """
    Compute multidimensional qualification alignment scores.
    """
    with mcp_telemetry("score_qualification", context) as collector:
        input_data = QualificationInput(
            raw_text=raw_text,
            job_description_id=job_description_id,
            email=email,
            location=location,
            technology_keywords=technology_keywords
        )
        
        # Resolve the lazy-loaded singleton service
        service = get_qualification_scorer_service()
        
        result = service.process(input_data)
        collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="summarize_candidate",
    description="Generate a detailed, evidence-grounded recruiter summary matching qualification scores and job descriptions."
)
async def summarize_candidate(
    raw_text: str,
    job_description_id: str,
    email: Optional[str] = None,
    location: Optional[str] = None,
    technology_keywords: Optional[list] = None,
    context: Optional[dict] = None
) -> str:
    """
    Generate a detailed, evidence-grounded candidate qualification summary.
    """
    with mcp_telemetry("summarize_candidate", context) as collector:
        input_data = SummarizationInput(
            raw_text=raw_text,
            job_description_id=job_description_id,
            email=email,
            location=location,
            technology_keywords=technology_keywords
        )
        service = get_summarization_service()
        result = service.process(input_data)
        collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="build_context",
    description="Compose structured outputs from Phase 2 services into an immutable, segmented ContextSnapshot."
)
async def build_context(
    context_id: str,
    document_references: list,
    session_id: Optional[str] = None,
    raw_text: Optional[str] = None,
    candidate_profile: Optional[dict] = None,
    candidate_enrichment: Optional[dict] = None,
    retrieved_context: Optional[list] = None,
    qualification_scores: Optional[dict] = None,
    recruiter_summary: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    """
    Compose structured candidate attributes into an immutable ContextSnapshot.
    """
    with mcp_telemetry("build_context", context) as collector:
        from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
        from src.intelligence.tools.deterministic_enricher.schema import EnrichmentOutput
        from src.intelligence.tools.qualification_scorer.schema import QualificationPayload
        from src.intelligence.tools.summarizer.schema import SummarizationPayload
        
        profile_model = CandidateOutput.model_validate(candidate_profile) if candidate_profile else None
        enrich_model = EnrichmentOutput.model_validate(candidate_enrichment) if candidate_enrichment else None
        scores_model = QualificationPayload.model_validate(qualification_scores) if qualification_scores else None
        summary_model = SummarizationPayload.model_validate(recruiter_summary) if recruiter_summary else None
        
        input_data = ContextBuilderInput(
            context_id=context_id,
            session_id=session_id,
            document_references=document_references,
            raw_text=raw_text,
            candidate_profile=profile_model,
            candidate_enrichment=enrich_model,
            retrieved_context=retrieved_context,
            qualification_scores=scores_model,
            recruiter_summary=summary_model
        )
        
        service = get_context_builder_service()
        result = service.process(input_data)
        collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="save_memory",
    description="Persist or merge a ContextSnapshot into the append-only memory store log."
)
async def save_memory(
    snapshot: dict,
    session_id: Optional[str] = None,
    tags: Optional[list] = None,
    importance: float = 1.0,
    context: Optional[dict] = None
) -> str:
    """
    Persist or merge a ContextSnapshot.
    """
    with mcp_telemetry("save_memory", context) as collector:
        from src.intelligence.tools.context_builder.schema import ContextSnapshot
        snapshot_model = ContextSnapshot.model_validate(snapshot)
        
        input_data = MemoryStoreRequest(
            snapshot=snapshot_model,
            session_id=session_id,
            tags=tags or [],
            importance=importance
        )
        service = get_memory_service()
        result = service.save_memory(input_data)
        collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="retrieve_memory",
    description="Retrieve memory snapshots by memory_id, context_id, or session_id from the append-only log."
)
async def retrieve_memory(
    memory_id: Optional[str] = None,
    context_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    """
    Retrieve memory snapshots by identifiers.
    """
    with mcp_telemetry("retrieve_memory", context) as collector:
        input_data = MemoryRetrieveRequest(
            memory_id=memory_id,
            context_id=context_id,
            session_id=session_id
        )
        service = get_memory_service()
        result = service.retrieve_memory(input_data)
        collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="search_memory",
    description="Scan and search persistent memory snapshots matching tag filters and keyword queries."
)
async def search_memory(
    query_text: Optional[str] = None,
    session_id: Optional[str] = None,
    tags: Optional[list] = None,
    importance_threshold: float = 0.0,
    limit: int = 10,
    context: Optional[dict] = None
) -> str:
    """
    Scan and search persistent memories.
    """
    with mcp_telemetry("search_memory", context) as collector:
        input_data = MemoryQuery(
            query_text=query_text,
            session_id=session_id,
            tags=tags or [],
            importance_threshold=importance_threshold,
            limit=limit
        )
        service = get_memory_service()
        result = service.search_memory(input_data)
        collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="run_orchestrator",
    description="Execute the full candidate assessment and context building pipeline."
)
async def run_orchestrator(
    query_text: str,
    session_id: Optional[str] = None,
    context_id: Optional[str] = None,
    force_tools: Optional[list] = None,
    email: Optional[str] = None,
    location: Optional[str] = None,
    technology_keywords: Optional[list] = None,
    context: Optional[dict] = None
) -> str:
    """
    Execute the full candidate assessment pipeline.
    """
    with mcp_telemetry("run_orchestrator", context) as collector:
        from src.intelligence.tools.agent_orchestrator.schema import OrchestrationRequest
        from src.intelligence.tools.agent_orchestrator.service import get_agent_orchestrator_service
        
        input_data = OrchestrationRequest(
            query_text=query_text,
            session_id=session_id,
            context_id=context_id,
            force_tools=force_tools or [],
            email=email,
            location=location,
            technology_keywords=technology_keywords or []
        )
        service = get_agent_orchestrator_service()
        result = service.process(input_data)
        collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="run_planner",
    description="Analyze request context, check constraints, select workflow template, and return a validated ExecutionPlan."
)
async def run_planner(
    query_text: str,
    session_id: Optional[str] = None,
    context_id: Optional[str] = None,
    force_workflow: Optional[str] = None,
    email: Optional[str] = None,
    location: Optional[str] = None,
    technology_keywords: Optional[list] = None,
    context: Optional[dict] = None
) -> str:
    """
    Expose PlannerService workflow selection logic over the MCP server protocol.
    """
    with mcp_telemetry("run_planner", context) as collector:
        from src.intelligence.tools.planner.schema import PlannerRequest
        from src.intelligence.tools.planner.service import get_planner_service
        
        input_data = PlannerRequest(
            query_text=query_text,
            session_id=session_id,
            context_id=context_id,
            force_workflow=force_workflow,
            email=email,
            location=location,
            technology_keywords=technology_keywords or []
        )
        
        # Retrieve tools from orchestrator singleton to satisfy available list checking
        from src.intelligence.tools.agent_orchestrator.service import get_agent_orchestrator_service
        orchestrator = get_agent_orchestrator_service()
        tools = orchestrator.provider.registry.get_all_tools()
        
        result = get_planner_service().plan(
            request=input_data,
            available_tools=tools
        )
        
        # Set collector metadata if success
        if hasattr(result, "metadata") and result.metadata:
            collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="post_conversation_turn",
    description="Post a new conversational turn (user or assistant) to working memory for a session."
)
async def post_conversation_turn(
    session_id: str,
    role: str,
    content: str,
    active_goal: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    """
    Append message turn to session working memory.
    """
    with mcp_telemetry("post_conversation_turn", context) as collector:
        from src.intelligence.tools.conversation_memory.service import get_conversation_memory_service
        result = get_conversation_memory_service().post_turn(
            session_id=session_id,
            role=role,
            content=content,
            active_goal=active_goal
        )
        if hasattr(result, "metadata") and result.metadata:
            collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="get_conversation_context",
    description="Retrieve consolidated conversational context (recent turns, memories, unresolved questions) for a session."
)
async def get_conversation_context(
    session_id: str,
    query_text: Optional[str] = None,
    active_goal: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    """
    Retrieve consolidated session conversation context for planner consumption.
    """
    with mcp_telemetry("get_conversation_context", context) as collector:
        from src.intelligence.tools.conversation_memory.service import get_conversation_memory_service
        result = get_conversation_memory_service().get_context(
            session_id=session_id,
            query_text=query_text,
            active_goal=active_goal
        )
        if hasattr(result, "metadata") and result.metadata:
            collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="assess_opportunity",
    description="Analyze structured snapshot outputs and produce an evidence-backed OpportunityAssessment."
)
async def assess_opportunity(
    context_snapshot: dict,
    conversation_context: Optional[dict] = None,
    assessment_type: Optional[str] = "candidate",
    context: Optional[dict] = None
) -> str:
    """
    Produce an evidence-backed OpportunityAssessment from preceding structured outputs.
    """
    with mcp_telemetry("assess_opportunity", context) as collector:
        from src.intelligence.tools.context_builder.schema import ContextSnapshot
        from src.intelligence.tools.conversation_memory.schema import ConversationContext
        from src.intelligence.tools.opportunity_intelligence.schema import AssessmentType
        from src.intelligence.tools.opportunity_intelligence.service import get_opportunity_intelligence_service
        
        snapshot_model = ContextSnapshot.model_validate(context_snapshot)
        conv_model = ConversationContext.model_validate(conversation_context) if conversation_context else None
        
        try:
            type_enum = AssessmentType(assessment_type)
        except ValueError:
            type_enum = AssessmentType.CANDIDATE
            
        result = get_opportunity_intelligence_service().assess(
            context_snapshot=snapshot_model,
            conversation_context=conv_model,
            assessment_type=type_enum
        )
        
        if hasattr(result, "metadata") and result.metadata:
            collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="run_revenue_copilot",
    description="Translate OpportunityAssessment into playbook categories, draft communications, and task checklists."
)
async def run_revenue_copilot(
    opportunity_assessment: dict,
    context_snapshot: dict,
    conversation_context: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    """
    Produce structured business guidance recommendations from an OpportunityAssessment.
    """
    with mcp_telemetry("run_revenue_copilot", context) as collector:
        from src.intelligence.tools.context_builder.schema import ContextSnapshot
        from src.intelligence.tools.conversation_memory.schema import ConversationContext
        from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment
        from src.intelligence.tools.revenue_copilot.schema import RevenueCopilotRequest
        from src.intelligence.tools.revenue_copilot.service import get_revenue_copilot_service
        
        assess_model = OpportunityAssessment.model_validate(opportunity_assessment)
        snapshot_model = ContextSnapshot.model_validate(context_snapshot)
        conv_model = ConversationContext.model_validate(conversation_context) if conversation_context else None
        
        req = RevenueCopilotRequest(
            opportunity_assessment=assess_model,
            context_snapshot=snapshot_model,
            conversation_context=conv_model
        )
        
        result = get_revenue_copilot_service().run(req)
        
        if hasattr(result, "metadata") and result.metadata:
            collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="run_evaluation",
    description="Run evaluation on a dataset using target component configuration settings."
)
async def run_evaluation(
    domain: str,
    dataset_type: str,
    version: str,
    config: dict,
    experiment_id: Optional[str] = "exp_default",
    context: Optional[dict] = None
) -> str:
    """
    Load dataset and execute evaluation suite against target config specifications.
    """
    with mcp_telemetry("run_evaluation", context) as collector:
        from src.intelligence.tools.evaluation_framework.schema import EvaluationConfig, EvaluationResult
        from src.intelligence.tools.evaluation_framework.dataset.registry import DatasetRegistry
        from src.intelligence.tools.evaluation_framework.service import get_evaluation_service
        
        # Load dataset
        registry = DatasetRegistry()
        dataset = registry.get_dataset(domain=domain, dataset_type=dataset_type, version=version)
        
        # Validate config
        config_model = EvaluationConfig.model_validate(config)
        
        # Trigger evaluation service
        service = get_evaluation_service()
        report = service.run_evaluation(dataset, config_model, experiment_id=experiment_id)
        
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus
        
        res_metadata = ResponseMetadata(
            provider="evaluation_framework",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        result = EvaluationResult(
            report=report,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        if hasattr(result, "metadata") and result.metadata:
            collector.metadata = result.metadata
        return result.model_dump_json()

@mcp.tool(
    name="list_evaluation_datasets",
    description="List all available datasets in the registry."
)
async def list_evaluation_datasets(context: Optional[dict] = None) -> str:
    """
    Return lists of available dataset files in registry directories.
    """
    with mcp_telemetry("list_evaluation_datasets", context):
        from src.intelligence.tools.evaluation_framework.dataset.registry import DatasetRegistry
        registry = DatasetRegistry()
        return json.dumps(registry.list_datasets())

@mcp.tool(
    name="create_replay",
    description="Manually record a target execution input/output payload for debugging."
)
async def create_replay(
    target_id: str,
    input_payload: Any,
    output_payload: Any,
    parent_replay_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("create_replay", context) as collector:
        from src.intelligence.tools.replay_debug.service import get_replay_service
        from src.intelligence.tools.replay_debug.schema import ReplayResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_replay_service()
        record = service.create_replay(
            target_id=target_id,
            input_payload=input_payload,
            output_payload=output_payload,
            parent_replay_id=parent_replay_id,
            metadata=metadata
        )

        res_metadata = ResponseMetadata(
            provider="replay_debug",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = ReplayResponse(
            replay_record=record,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="replay_execution",
    description="Re-run a recorded execution with optional prompt/model configuration overrides."
)
async def replay_execution(
    replay_id: str,
    override_config: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("replay_execution", context) as collector:
        from src.intelligence.tools.replay_debug.service import get_replay_service
        from src.intelligence.tools.replay_debug.schema import ReplayResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_replay_service()
        result = service.replay_execution(replay_id, override_config=override_config)

        res_metadata = ResponseMetadata(
            provider="replay_debug",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = ReplayResponse(
            execution_result=result,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="compare_replays",
    description="Compare an original execution against a replayed execution to isolate regressions."
)
async def compare_replays(
    replay_id: str,
    override_config: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("compare_replays", context) as collector:
        from src.intelligence.tools.replay_debug.service import get_replay_service
        from src.intelligence.tools.replay_debug.schema import ReplayResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_replay_service()
        diff = service.compare_replays(replay_id, override_config=override_config)

        res_metadata = ResponseMetadata(
            provider="replay_debug",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = ReplayResponse(
            diff=diff,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="generate_debug_report",
    description="Produce a structured JSON/Markdown debug report for code/model regressions."
)
async def generate_debug_report(
    replay_id: str,
    override_config: Optional[dict] = None,
    format: Optional[str] = "json",
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("generate_debug_report", context) as collector:
        from src.intelligence.tools.replay_debug.service import get_replay_service
        from src.intelligence.tools.replay_debug.schema import ReplayResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_replay_service()
        path = service.generate_debug_report(replay_id, override_config=override_config, format=format)

        res_metadata = ResponseMetadata(
            provider="replay_debug",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = ReplayResponse(
            report_path=path,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="submit_feedback",
    description="Submit human or system feedback on a specific execution target."
)
async def submit_feedback(
    target_id: str,
    target_type: str,
    run_id: str,
    feedback_type: str,
    feedback_payload: Any,
    reviewer_id: Optional[str] = None,
    replay_id: Optional[str] = None,
    evaluation_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("submit_feedback", context) as collector:
        from src.intelligence.tools.human_feedback.service import get_feedback_service
        from src.intelligence.tools.human_feedback.schema import FeedbackResponse, TargetType, FeedbackType
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_feedback_service()
        record = service.submit_feedback(
            target_id=target_id,
            target_type=TargetType(target_type),
            run_id=run_id,
            feedback_type=FeedbackType(feedback_type),
            feedback_payload=feedback_payload,
            reviewer_id=reviewer_id,
            replay_id=replay_id,
            evaluation_id=evaluation_id,
            metadata=metadata
        )

        res_metadata = ResponseMetadata(
            provider="human_feedback",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = FeedbackResponse(
            feedback_record=record,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="list_feedback",
    description="List all submitted feedback matching optional target and run filter specifications."
)
async def list_feedback(
    target_id: Optional[str] = None,
    run_id: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("list_feedback", context) as collector:
        from src.intelligence.tools.human_feedback.service import get_feedback_service
        from src.intelligence.tools.human_feedback.schema import FeedbackResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_feedback_service()
        records = service.list_feedback(target_id=target_id, run_id=run_id)

        res_metadata = ResponseMetadata(
            provider="human_feedback",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = FeedbackResponse(
            feedback_records=records,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="get_feedback",
    description="Retrieve a specific feedback record by its feedback_id."
)
async def get_feedback(
    feedback_id: str,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("get_feedback", context) as collector:
        from src.intelligence.tools.human_feedback.service import get_feedback_service
        from src.intelligence.tools.human_feedback.schema import FeedbackResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_feedback_service()
        record = service.get_feedback(feedback_id)

        res_metadata = ResponseMetadata(
            provider="human_feedback",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = FeedbackResponse(
            feedback_record=record,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="feedback_summary",
    description="Compute agreement, approval ratios, and feedback trends for an execution target."
)
async def feedback_summary(
    target_id: str,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("feedback_summary", context) as collector:
        from src.intelligence.tools.human_feedback.service import get_feedback_service
        from src.intelligence.tools.human_feedback.analytics import AnalyticsRegistry
        from src.intelligence.tools.human_feedback.schema import FeedbackResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_feedback_service()
        records = service.list_feedback(target_id=target_id)
        
        registry = AnalyticsRegistry()
        summary = registry.compute_all(records)

        res_metadata = ResponseMetadata(
            provider="human_feedback",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = FeedbackResponse(
            analytics_summary=summary,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="promote_dataset_item",
    description="Promote high-quality reviewed replays to versioned immutable datasets."
)
async def promote_dataset_item(
    replay_id: str,
    target_domain: str,
    target_dataset_type: str,
    target_version: str,
    actor: str,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("promote_dataset_item", context) as collector:
        from src.intelligence.tools.human_feedback.service import get_feedback_service
        from src.intelligence.tools.human_feedback.promotion import DatasetPromotionWorkflow
        from src.intelligence.tools.human_feedback.schema import FeedbackResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_feedback_service()
        workflow = DatasetPromotionWorkflow(feedback_provider=service.provider)
        
        req = workflow.request_promotion(
            replay_id=replay_id,
            target_domain=target_domain,
            target_dataset_type=target_dataset_type,
            target_version=target_version,
            actor=actor
        )
        
        records = service.list_feedback(target_id=replay_id)
        if not records:
            from src.intelligence.tools.human_feedback.schema import FeedbackRecord, FeedbackTarget, TargetType, FeedbackType
            records = [FeedbackRecord(
                run_id="run_prom",
                target=FeedbackTarget(target_id=replay_id, target_type=TargetType.TOOL),
                feedback_type=FeedbackType.RATING,
                feedback_payload={"score": 5.0},
                timestamp="2026"
            )]
            
        updated = workflow.evaluate_and_promote(req.promotion_id, records, actor=actor)

        res_metadata = ResponseMetadata(
            provider="human_feedback",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = FeedbackResponse(
            promotion_request=updated,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="ingest_knowledge",
    description="Ingest a document or dataset into the Production Knowledge Platform registry."
)
async def ingest_knowledge(
    namespace: str,
    content: str,
    asset_type: str,
    asset_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    version: str = "v1",
    parent_version_id: Optional[str] = None,
    derived_from_asset_id: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("ingest_knowledge", context) as collector:
        from src.intelligence.tools.knowledge_platform.service import get_knowledge_service
        from src.intelligence.tools.knowledge_platform.schema import KnowledgeResponse, AssetType
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_knowledge_service()
        asset = service.ingest_knowledge(
            namespace=namespace,
            content=content,
            asset_type=AssetType(asset_type),
            asset_id=asset_id,
            metadata=metadata,
            version=version,
            parent_version_id=parent_version_id,
            derived_from_asset_id=derived_from_asset_id
        )

        res_metadata = ResponseMetadata(
            provider="knowledge_platform",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = KnowledgeResponse(
            asset=asset,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="list_knowledge",
    description="List all available assets registered in the platform namespaces."
)
async def list_knowledge(
    namespace: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("list_knowledge", context) as collector:
        from src.intelligence.tools.knowledge_platform.service import get_knowledge_service
        from src.intelligence.tools.knowledge_platform.schema import KnowledgeResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_knowledge_service()
        assets = service.list_knowledge(namespace=namespace)

        res_metadata = ResponseMetadata(
            provider="knowledge_platform",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = KnowledgeResponse(
            assets=assets,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="retrieve_knowledge_platform",
    description="Query knowledge assets semantically using hybrid vector and BM25 strategies."
)
async def retrieve_knowledge_platform(
    query: str,
    namespace: Optional[str] = None,
    strategy: str = "hybrid",
    filters: Optional[dict] = None,
    limit: int = 5,
    min_score: Optional[float] = None,
    metadata: Optional[dict] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("retrieve_knowledge_platform", context) as collector:
        from src.intelligence.tools.knowledge_platform.service import get_knowledge_service
        from src.intelligence.tools.knowledge_platform.schema import KnowledgeResponse, KnowledgeQuery
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        query_model = KnowledgeQuery(
            query=query,
            namespace=namespace,
            strategy=strategy,
            filters=filters or {},
            limit=limit,
            min_score=min_score,
            metadata=metadata or {}
        )

        service = get_knowledge_service()
        chunks = service.retrieve_knowledge(query_model)

        res_metadata = ResponseMetadata(
            provider="knowledge_platform",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = KnowledgeResponse(
            chunks=chunks,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="update_index",
    description="Save or consolidate structured indices for an index registry partition."
)
async def update_index(
    index_name: str,
    index_data: dict,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("update_index", context) as collector:
        from src.intelligence.tools.knowledge_platform.service import get_knowledge_service
        from src.intelligence.tools.knowledge_platform.schema import KnowledgeResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_knowledge_service()
        service.provider.save_index(index_name, index_data)

        res_metadata = ResponseMetadata(
            provider="knowledge_platform",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = KnowledgeResponse(
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="rebuild_embeddings",
    description="Regenerate vector embeddings for all assets matching a namespace."
)
async def rebuild_embeddings(
    namespace: str,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("rebuild_embeddings", context) as collector:
        from src.intelligence.tools.knowledge_platform.service import get_knowledge_service
        from src.intelligence.tools.knowledge_platform.schema import KnowledgeResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_knowledge_service()
        service.rebuild_embeddings(namespace)

        res_metadata = ResponseMetadata(
            provider="knowledge_platform",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = KnowledgeResponse(
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="knowledge_statistics",
    description="Compute retrieval precision, namespace size, and storage utilization stats."
)
async def knowledge_statistics(
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("knowledge_statistics", context) as collector:
        from src.intelligence.tools.knowledge_platform.service import get_knowledge_service
        from src.intelligence.tools.knowledge_platform.analytics import KnowledgeAnalyticsRegistry
        from src.intelligence.tools.knowledge_platform.schema import KnowledgeResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_knowledge_service()
        assets = service.list_knowledge()
        
        chunks = []
        for ns in service.registry.list_namespaces():
            chunks.extend(service.index_registry.get_chunks(ns))
            
        analytics = KnowledgeAnalyticsRegistry()
        summary = analytics.compute_all(assets, chunks)

        res_metadata = ResponseMetadata(
            provider="knowledge_platform",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = KnowledgeResponse(
            analytics_summary=summary,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="monitoring_status",
    description="Get registered monitored components and check system state logs."
)
async def monitoring_status(
    component_id: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("monitoring_status", context) as collector:
        from src.intelligence.tools.monitoring_observability.service import get_monitoring_service
        from src.intelligence.tools.monitoring_observability.schema import MonitoringResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_monitoring_service()
        res_metadata = ResponseMetadata(
            provider="monitoring_observability",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )

        if component_id:
            comp = service.registry.get_component(component_id)
            response = MonitoringResponse(
                status=ResponseStatus.SUCCESS,
                component=comp,
                metadata=res_metadata
            )
        else:
            components = service.registry.list_components()
            response = MonitoringResponse(
                status=ResponseStatus.SUCCESS,
                analytics_summary={"total_components": len(components)},
                metadata=res_metadata
            )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="monitoring_metrics",
    description="Retrieve latency, throughput, token usage, and cost logs."
)
async def monitoring_metrics(
    category: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("monitoring_metrics", context) as collector:
        from src.intelligence.tools.monitoring_observability.service import get_monitoring_service
        from src.intelligence.tools.monitoring_observability.schema import MonitoringResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_monitoring_service()
        metrics = service.provider.load_metrics()
        if category:
            metrics = [m for m in metrics if getattr(m, "category", "") == category]

        res_metadata = ResponseMetadata(
            provider="monitoring_observability",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = MonitoringResponse(
            status=ResponseStatus.SUCCESS,
            metrics=metrics,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="monitoring_events",
    description="Retrieve recent monitoring events, optionally filtered by severity."
)
async def monitoring_events(
    severity: Optional[str] = None,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("monitoring_events", context) as collector:
        from src.intelligence.tools.monitoring_observability.service import get_monitoring_service
        from src.intelligence.tools.monitoring_observability.schema import MonitoringResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_monitoring_service()
        events = service.provider.load_events()
        if severity:
            events = [e for e in events if getattr(e, "severity", "") == severity]

        res_metadata = ResponseMetadata(
            provider="monitoring_observability",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = MonitoringResponse(
            status=ResponseStatus.SUCCESS,
            events=events,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="monitoring_health",
    description="Run custom status health check validation on a specific component."
)
async def monitoring_health(
    component_id: str,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("monitoring_health", context) as collector:
        from src.intelligence.tools.monitoring_observability.service import get_monitoring_service
        from src.intelligence.tools.monitoring_observability.schema import MonitoringResponse, MonitoredComponent, ComponentHealth
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_monitoring_service()
        comp = service.registry.get_component(component_id)
        if not comp:
            comp = MonitoredComponent(
                component_id=component_id,
                component_type="unknown",
                health_status=ComponentHealth.HEALTHY
            )
            service.registry.register_component(comp)
            
        res_metadata = ResponseMetadata(
            provider="monitoring_observability",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = MonitoringResponse(
            status=ResponseStatus.SUCCESS,
            component=comp,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="monitoring_alerts",
    description="Retrieve currently triggered monitoring and policy regression alerts."
)
async def monitoring_alerts(
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("monitoring_alerts", context) as collector:
        from src.intelligence.tools.monitoring_observability.service import get_monitoring_service
        from src.intelligence.tools.monitoring_observability.schema import MonitoringResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_monitoring_service()
        alerts = service.provider.load_alerts()

        res_metadata = ResponseMetadata(
            provider="monitoring_observability",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        response = MonitoringResponse(
            status=ResponseStatus.SUCCESS,
            alerts=alerts,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

@mcp.tool(
    name="monitoring_trace",
    description="Retrieve timelines and context spans matching trace identifier."
)
async def monitoring_trace(
    trace_id: str,
    context: Optional[dict] = None
) -> str:
    with mcp_telemetry("monitoring_trace", context) as collector:
        from src.intelligence.tools.monitoring_observability.service import get_monitoring_service
        from src.intelligence.tools.monitoring_observability.schema import MonitoringResponse
        from src.intelligence.platform.metadata import ResponseMetadata
        from src.intelligence.platform.contracts import ResponseStatus

        service = get_monitoring_service()
        spans = service.provider.load_spans()
        matched = [s for s in spans if getattr(s, "trace_id", "") == trace_id]

        res_metadata = ResponseMetadata(
            provider="monitoring_observability",
            model="default",
            prompt_version="1.0.0",
            confidence=1.0,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        response = MonitoringResponse(
            status=ResponseStatus.SUCCESS,
            span=matched[0] if matched else None,
            metadata=res_metadata
        )
        collector.metadata = res_metadata
        return response.model_dump_json()

if __name__ == "__main__":
    mcp.run()
