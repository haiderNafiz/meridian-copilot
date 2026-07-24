import json
from src.intelligence.platform.contracts import ResponseStatus
from src.intelligence.platform.metadata import ResponseMetadata
from src.intelligence.tools.qualification_scorer.schema import QualificationInput, ScoringDimension
from .schema import SummarizationInput, SummarizationOutput, SummaryType

class SummarizationService:
    def __init__(
        self,
        qualification_scorer_service,
        summarizer_provider
    ):
        self.qualification_scorer_service = qualification_scorer_service
        self.summarizer_provider = summarizer_provider

    def process(self, request: SummarizationInput) -> SummarizationOutput:
        if request.summary_type != SummaryType.CANDIDATE:
            raise NotImplementedError(f"Summary type {request.summary_type} not yet implemented")

        # 1. Invoke Qualification Scorer façade (returns profile, enrichment, context, and scores)
        score_res = self.qualification_scorer_service.process(QualificationInput(
            raw_text=request.raw_text,
            job_description_id=request.job_description_id,
            email=request.email,
            location=request.location,
            technology_keywords=request.technology_keywords
        ))
        
        # 2. Package context structured details into JSON mapping (No duplicate retrievals or orchestration)
        context_dict = {
            "candidate_profile": score_res.candidate_profile.model_dump() if score_res.candidate_profile else {},
            "candidate_enrichment": score_res.candidate_enrichment.model_dump() if score_res.candidate_enrichment else {},
            "retrieved_context": [c.model_dump() for c in score_res.retrieved_context] if score_res.retrieved_context else [],
            "qualification_scores": score_res.payload.model_dump()
        }
        context_json = json.dumps(context_dict, indent=2)
        
        # 3. Request LLM Inference
        payload, prompt_version = self.summarizer_provider.infer(request.summary_type, context_json)
        
        # 4. Formulate audit meta sequence
        provider_chain = score_res.provider_chain + [self.summarizer_provider.__class__.__name__]
        
        metadata = ResponseMetadata(
            provider="groq",
            model="llama-3.3-70b-versatile",
            prompt_version=prompt_version,
            confidence=score_res.payload.scores[ScoringDimension.OVERALL_QUALIFICATION].confidence,
            fallback_used=False,
            provider_latency_ms=0.0
        )
        
        return SummarizationOutput(
            status=ResponseStatus.SUCCESS,
            metadata=metadata,
            payload=payload,
            provider_chain=provider_chain,
            retrieved_chunks=score_res.retrieved_chunks
        )

_summarizer_service_instance = None

def get_summarization_service() -> SummarizationService:
    global _summarizer_service_instance
    if _summarizer_service_instance is None:
        from src.intelligence.platform.clients import LLMClientFactory
        from src.intelligence.tools.qualification_scorer.service import get_qualification_scorer_service
        from .provider import SummarizationProvider
        
        scorer_service = get_qualification_scorer_service()
        client = LLMClientFactory.get_groq_client()
        provider = SummarizationProvider(client=client)
        
        _summarizer_service_instance = SummarizationService(
            qualification_scorer_service=scorer_service,
            summarizer_provider=provider
        )
    return _summarizer_service_instance
