import os
import json
from pathlib import Path
from typing import Tuple
from src.intelligence.platform.config import PlatformConfig
from src.intelligence.platform.prompts import PromptLoader
from .schema import SummarizationPayload, SummaryType

class SummarizationProvider:
    def __init__(self, client):
        self.client = client
        config = PlatformConfig.load()
        self.model = config.groq_model
        
    def _load_prompts(self, summary_type: SummaryType) -> Tuple[str, str]:
        dir_path = Path(os.path.dirname(os.path.abspath(__file__)))
        prompts_dir = dir_path / "prompts" / summary_type.value
        
        # Load via standard PromptLoader
        prompt_obj = PromptLoader.load(str(prompts_dir))
        return prompt_obj.text, prompt_obj.version

    def infer(
        self,
        summary_type: SummaryType,
        context_json: str
    ) -> Tuple[SummarizationPayload, str]:
        prompt_template, version = self._load_prompts(summary_type)
        
        # Inject dynamic JSON variable
        user_prompt = prompt_template.replace("{{ candidate_context_json }}", context_json)
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            model=self.model,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        content = chat_completion.choices[0].message.content
        parsed = json.loads(content)
        
        payload = SummarizationPayload.model_validate(parsed)
        return payload, version
