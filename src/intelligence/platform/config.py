import os

class PlatformConfig:
    def __init__(self):
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self.groq_model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    _instance = None

    @classmethod
    def load(cls) -> "PlatformConfig":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
