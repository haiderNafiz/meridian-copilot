from typing import List, Optional
from src.intelligence.platform.contracts import ResponseStatus
from src.intelligence.platform.metadata import ResponseMetadata
from src.intelligence.tools.candidate_profiler.schema import CandidateInput
from src.intelligence.tools.deterministic_enricher.schema import EnrichmentInput
from src.intelligence.tools.knowledge_service.schema import RetrievalInput
from .schema import QualificationInput, QualificationOutput, ScoringDimension

class QualificationScorerService:
    def __init__(
        self,
        profiler_service,
        enrichment_service,
        retrieval_service,
        scorer_provider
    ):
        self.profiler_service = profiler_service
        self.enrichment_service = enrichment_service
        self.retrieval_service = retrieval_service
        self.scorer_provider = scorer_provider

    def process(self, request: QualificationInput) -> QualificationOutput:
        # Step 1: Profile raw candidate text
        profile_res, _ = self.profiler_service.profile(CandidateInput(
            raw_text=request.raw_text,
            technology_keywords=request.technology_keywords
        ))
        
        # Step 2: Normalize fields deterministically
        enrich_res = self.enrichment_service.process(EnrichmentInput(
            email=request.email,
            location=request.location,
            technology_keywords=request.technology_keywords
        ))
        
        # Step 3: Query Knowledge Platform
        # TODO (Phase 3 Optimization):
        # Once utilizing a real vector DB, improve query matching by compiling candidate details semantically,
        # e.g., query = f"{profile_res.role_type} {profile_res.technical_domains} {profile_res.predicted_functions}"
        # instead of searching with a job ID string.
        retrieval_res = self.retrieval_service.process(RetrievalInput(
            query=f"Requirements for job {request.job_description_id}",
            collection="job_descriptions",
            filters={"document_id": request.job_description_id},
            limit=3
        ))
        
        # Step 4: Call LLM Scoring Provider
        payload, prompt_version = self.scorer_provider.infer(profile_res, enrich_res, retrieval_res.payload)
        
        # Step 5: Build dynamic audit provider chain and chunk lists
        retrieved_chunk_ids = [r.metadata.chunk_id for r in retrieval_res.payload.results]
        provider_chain = [
            self.profiler_service.__class__.__name__,
            self.enrichment_service.__class__.__name__,
            self.retrieval_service.__class__.__name__,
            self.scorer_provider.__class__.__name__
        ]
        
        metadata = ResponseMetadata(
            provider="groq",
            model="llama-3.3-70b-versatile",
            prompt_version=prompt_version,
            confidence=payload.scores[ScoringDimension.OVERALL_QUALIFICATION].confidence,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        return QualificationOutput(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            payload=payload,
            retrieved_chunks=retrieved_chunk_ids,
            provider_chain=provider_chain,
            candidate_profile=profile_res,
            candidate_enrichment=enrich_res,
            retrieved_context=retrieval_res.payload.results
        )

_service_instance = None

def get_qualification_scorer_service():
    global _service_instance
    if _service_instance is None:
        from src.intelligence.platform.config import PlatformConfig
        from src.intelligence.platform.clients import LLMClientFactory
        from src.intelligence.tools.candidate_profiler.profiler import get_candidate_profiler_service
        from src.intelligence.tools.deterministic_enricher.service import DeterministicEnrichmentService
        from src.intelligence.tools.knowledge_service.service import RetrievalService
        from src.intelligence.tools.knowledge_service.provider import RetrievalProvider
        # TODO (Phase 3):
        # Replace MockVectorStore with production VectorStore implementation (e.g. Chroma/Qdrant)
        # via dependency injection without changing QualificationScorerService.
        from src.intelligence.tools.knowledge_service.store.mock_store import MockVectorStore
        from src.intelligence.tools.knowledge_service.embedding.mock_embed import MockEmbeddingProvider
        from src.intelligence.tools.knowledge_service.ranking.cosine import CosineSimilarityRanker
        from .provider import QualificationProvider
        
        config = PlatformConfig.load()
        
        profiler = get_candidate_profiler_service()
        enricher = DeterministicEnrichmentService()
        
        # Storage-agnostic vector store dependency injection
        store = MockVectorStore()
        embedder = MockEmbeddingProvider()
        ranker = CosineSimilarityRanker()
        retrieval = RetrievalService(provider=RetrievalProvider(store, embedder, ranker))
        
        # Scorer Provider
        client = LLMClientFactory.get_groq_client()
        provider = QualificationProvider(client=client)
        
        _service_instance = QualificationScorerService(
            profiler_service=profiler,
            enrichment_service=enricher,
            retrieval_service=retrieval,
            scorer_provider=provider
        )
    return _service_instance
