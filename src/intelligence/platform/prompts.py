from pathlib import Path
from pydantic import BaseModel
from .errors import PromptLoadError

class Prompt(BaseModel):
    text: str
    version: str

class PromptLoader:
    @staticmethod
    def load(directory_path: str) -> Prompt:
        """
        Dynamically loads the prompt.txt and accompanying version.txt from the specified directory path.
        """
        dir_path = Path(directory_path)
        prompt_path = dir_path / "prompt.txt"
        version_path = dir_path / "version.txt"
        
        if not prompt_path.exists():
            raise PromptLoadError(f"Prompt template file not found at: {prompt_path}")
            
        try:
            prompt_text = prompt_path.read_text(encoding="utf-8")
                
            # Default to "1.0.0" if version.txt is missing
            version = "1.0.0"
            if version_path.exists():
                version = version_path.read_text(encoding="utf-8").strip()
                    
            return Prompt(text=prompt_text, version=version)
        except Exception as exc:
            raise PromptLoadError(f"Failed to load prompt from directory '{directory_path}': {str(exc)}")
