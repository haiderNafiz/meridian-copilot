import os
import json
from typing import Tuple
from pathlib import Path
from src.intelligence.platform.clients import LLMClientFactory
from src.intelligence.platform.config import PlatformConfig
from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
from src.intelligence.tools.deterministic_enricher.schema import EnrichmentOutput
from src.intelligence.tools.knowledge_service.schema import RetrievalPayload
from .schema import QualificationPayload

class QualificationProvider:
    def __init__(self, client=None):
        self.client = client if client else LLMClientFactory.get_groq_client()
        
        config = PlatformConfig.load()
        self.model = config.groq_model
        
        # Load prompts
        dir_path = Path(os.path.dirname(os.path.abspath(__file__)))
        prompts_dir = dir_path / "prompts"
        
        self.system_prompt = (prompts_dir / "system.txt").read_text(encoding="utf-8")
        self.user_template = (prompts_dir / "user.txt").read_text(encoding="utf-8")
        self.prompt_version = (prompts_dir / "version.txt").read_text(encoding="utf-8").strip()

    def infer(
        self,
        profile: CandidateOutput,
        enrichment: EnrichmentOutput,
        retrieval: RetrievalPayload
    ) -> Tuple[QualificationPayload, str]:
        candidate_technologies = (enrichment.payload.technology_keywords.normalized_value 
                                  if (enrichment.payload.technology_keywords and enrichment.payload.technology_keywords.normalized_value is not None) 
                                  else [])
        candidate_timezone = (enrichment.payload.timezone.normalized_value 
                              if (enrichment.payload.timezone and enrichment.payload.timezone.normalized_value is not None) 
                              else "Not Provided")
        candidate_country = (enrichment.payload.country.normalized_value 
                             if (enrichment.payload.country and enrichment.payload.country.normalized_value is not None) 
                             else "Not Provided")
        
        user_prompt = self.user_template
        user_prompt = user_prompt.replace("{{ candidate_role_type }}", profile.role_type or "Not Provided")
        user_prompt = user_prompt.replace("{{ candidate_seniority }}", profile.seniority or "Not Provided")
        user_prompt = user_prompt.replace("{{ candidate_urgency }}", profile.urgency or "Not Provided")
        user_prompt = user_prompt.replace("{{ candidate_technical_domains }}", ", ".join(profile.technical_domains))
        user_prompt = user_prompt.replace("{{ candidate_predicted_functions }}", ", ".join(profile.predicted_functions))
        user_prompt = user_prompt.replace("{{ candidate_technologies }}", ", ".join(candidate_technologies))
        user_prompt = user_prompt.replace("{{ candidate_timezone }}", candidate_timezone)
        user_prompt = user_prompt.replace("{{ candidate_country }}", candidate_country)
        
        # Render retrieved chunks section
        chunks_str = ""
        for chunk in retrieval.results:
            chunks_str += f"* Chunk ID: {chunk.metadata.chunk_id}\n"
            chunks_str += f"  Content: \"{chunk.text}\"\n"
            chunks_str += f"  Source: {chunk.metadata.source}\n"
        user_prompt = user_prompt.replace("{{ retrieved_chunks_section }}", chunks_str)
        
        # Invoke Groq API
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=self.model,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = chat_completion.choices[0].message.content
        parsed = json.loads(content)
        
        # Validate output schema
        payload = QualificationPayload.model_validate(parsed)
        return payload, self.prompt_version
