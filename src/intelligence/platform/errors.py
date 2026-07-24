class MeridianError(Exception):
    """Base exception for all copilot errors."""
    pass

class ConfigurationError(MeridianError):
    """Raised when environment variables or configurations are missing/invalid."""
    pass

class LLMProviderError(MeridianError):
    """Base provider exception."""
    pass

class ProviderTimeoutError(LLMProviderError):
    """Raised when LLM model inference times out."""
    pass

class InferenceError(LLMProviderError):
    """Raised when an LLM provider request fails or returns invalid response."""
    pass

class PromptLoadError(MeridianError):
    """Raised when prompt text or version files fail to load."""
    pass

class PlatformValidationError(MeridianError):
    """Raised when inputs or outputs violate schema boundaries."""
    pass

class TransportError(MeridianError):
    """Raised when communication over the MCP transport layer drops."""
    pass
