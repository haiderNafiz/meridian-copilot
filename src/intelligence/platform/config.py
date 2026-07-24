import os
from pathlib import Path

class PlatformConfig:
    def __init__(self):
        self._load_dotenv()
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self.groq_model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    def _load_dotenv(self):
        current_dir = Path(__file__).resolve()
        for parent in [current_dir] + list(current_dir.parents):
            env_file = parent / ".env"
            if env_file.exists():
                try:
                    for line in env_file.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ:
                                os.environ[k] = v
                except Exception:
                    pass
                break

    _instance = None

    @classmethod
    def load(cls) -> "PlatformConfig":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
