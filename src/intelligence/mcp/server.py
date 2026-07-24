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

if __name__ == "__main__":
    # Start the server using stdio transport
    mcp.run()
