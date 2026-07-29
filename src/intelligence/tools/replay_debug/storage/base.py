from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..schema import ReplayRecord

class ReplayStorage(ABC):
    @abstractmethod
    def save_replay(self, replay: ReplayRecord) -> str:
        """Save a ReplayRecord and return the storage identifier/path."""
        pass

    @abstractmethod
    def get_replay(self, replay_id: str) -> Optional[ReplayRecord]:
        """Load a ReplayRecord by its unique identifier."""
        pass

    @abstractmethod
    def list_replays(self, filters: Dict[str, Any] = None) -> List[ReplayRecord]:
        """List all saved ReplayRecords matching optional filters."""
        pass
