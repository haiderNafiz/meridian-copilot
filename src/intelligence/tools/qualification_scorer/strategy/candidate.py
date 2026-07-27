from typing import List, Optional
from .base import QualificationStrategy
from ..schema import QualificationInput, QualificationOutput, ScoringDimension
from src.intelligence.platform.contracts import ResponseStatus
from src.intelligence.platform.metadata import ResponseMetadata
from src.intelligence.tools.candidate_profiler.schema import CandidateInput
from src.intelligence.tools.deterministic_enricher.schema import EnrichmentInput
from src.intelligence.tools.knowledge_service.schema import RetrievalInput

class CandidateQualificationStrategy(QualificationStrategy):
    def __init__(
        self,
        profiler_service = None,
        enrichment_service = None,
        retrieval_service = None,
        scorer_provider = None
    ):
        from src.intelligence.tools.candidate_profiler.profiler import get_candidate_profiler_service
        from src.intelligence.tools.deterministic_enricher.service import DeterministicEnrichmentService
        from src.intelligence.tools.knowledge_service.service import RetrievalService
        from src.intelligence.tools.knowledge_service.provider import RetrievalProvider
        from src.intelligence.tools.knowledge_service.store.mock_store import MockVectorStore
        from src.intelligence.tools.knowledge_service.embedding.mock_embed import MockEmbeddingProvider
        from src.intelligence.tools.knowledge_service.ranking.cosine import CosineSimilarityRanker
        from ..provider import QualificationProvider
        from src.intelligence.platform.clients import LLMClientFactory

        self.profiler_service = profiler_service or get_candidate_profiler_service()
        self.enrichment_service = enrichment_service or DeterministicEnrichmentService()
        
        if retrieval_service is None:
            store = MockVectorStore()
            embedder = MockEmbeddingProvider()
            ranker = CosineSimilarityRanker()
            self.retrieval_service = RetrievalService(provider=RetrievalProvider(store, embedder, ranker))
        else:
            self.retrieval_service = retrieval_service
            
        if scorer_provider is None:
            client = LLMClientFactory.get_groq_client()
            self.scorer_provider = QualificationProvider(client=client)
        else:
            self.scorer_provider = scorer_provider

    def qualify(self, request: QualificationInput) -> QualificationOutput:
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
