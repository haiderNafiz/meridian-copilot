from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..schema import KnowledgeAsset

class KnowledgeProvider(ABC):
    @abstractmethod
    def save_asset(self, asset: KnowledgeAsset) -> str:
        """Save a knowledge asset to filesystem or database storage."""
        pass

    @abstractmethod
    def get_asset(self, asset_id: str, version: str) -> Optional[KnowledgeAsset]:
        """Load a specific knowledge asset by ID and version."""
        pass

    @abstractmethod
    def save_index(self, index_name: str, index_data: Dict[str, Any]) -> str:
        """Persist structured indices."""
        pass

    @abstractmethod
    def load_index(self, index_name: str) -> Optional[Dict[str, Any]]:
        """Load structured indices."""
        pass
