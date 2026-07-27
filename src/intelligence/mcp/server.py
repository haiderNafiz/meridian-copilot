from fastmcp import FastMCP
from typing import Optional, List, Dict
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

if __name__ == "__main__":
    # Start the server using stdio transport
    mcp.run()
