from groq import Groq
from .config import PlatformConfig
from .errors import ConfigurationError

class LLMClientFactory:
    _groq_client = None

    @classmethod
    def get_groq_client(cls) -> Groq:
        if cls._groq_client is None:
            config = PlatformConfig.load()
            api_key = config.groq_api_key
            if not api_key:
                raise ConfigurationError("GROQ_API_KEY environment variable is not set")
            cls._groq_client = Groq(api_key=api_key)
        return cls._groq_client
