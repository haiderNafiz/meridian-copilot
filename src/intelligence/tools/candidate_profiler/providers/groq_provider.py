from .base import CandidateProfilerProvider
from ..schema import CandidateInput, CandidateOutput
from typing import Tuple
import os
import json
import time
from src.intelligence.platform.clients import LLMClientFactory
from src.intelligence.platform.config import PlatformConfig
from src.intelligence.platform.prompts import PromptLoader

class GroqProvider(CandidateProfilerProvider):
    def __init__(self):
        self.client = LLMClientFactory.get_groq_client()
        config = PlatformConfig.load()
        self.model = config.groq_model
        
        # Load prompt template and version utilizing centralized loader
        dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_obj = PromptLoader.load(dir_path)
        self.prompt_template = prompt_obj.text
        self.prompt_version = prompt_obj.version

    def profile(self, input_data: CandidateInput) -> Tuple[CandidateOutput, float]:
        # Formulate template replacement values
        current_title_val = input_data.current_title if input_data.current_title else "Not Provided"
        skills_val = ", ".join(input_data.skills) if input_data.skills else "Not Provided"
        years_exp_val = str(input_data.years_experience) if input_data.years_experience is not None else "Not Provided"
        
        if input_data.job_context:
            job_context_section = f"Target Job Context Alignment:\n- Job context requirements: {json.dumps(input_data.job_context)}"
        else:
            job_context_section = ""

        # Populate prompt template
        prompt = self.prompt_template
        prompt = prompt.replace("{{current_title}}", current_title_val)
        prompt = prompt.replace("{{skills}}", skills_val)
        prompt = prompt.replace("{{years_experience}}", years_exp_val)
        prompt = prompt.replace("{{raw_text}}", input_data.raw_text)
        prompt = prompt.replace("{{job_context_section}}", job_context_section)

        # Call Groq API measuring latency
        start_time = time.perf_counter()
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        provider_latency_ms = (time.perf_counter() - start_time) * 1000.0

        content = chat_completion.choices[0].message.content
        parsed = json.loads(content)
        
        # Validate output schema
        output = CandidateOutput(**parsed)
        return output, provider_latency_ms
