from typing import Any, Dict, List, Optional
from .schema import ReplayRecord
from .storage.base import ReplayStorage
from .storage.file import LocalFilesystemStorage

class ReplayRegistry:
    def __init__(self, storage: Optional[ReplayStorage] = None):
        self.storage = storage or LocalFilesystemStorage()

    def register_replay(self, replay: ReplayRecord) -> str:
        """Persist a new ReplayRecord to storage."""
        return self.storage.save_replay(replay)

    def get_replay(self, replay_id: str) -> Optional[ReplayRecord]:
        """Fetch a specific ReplayRecord by ID."""
        return self.storage.get_replay(replay_id)

    def find_replays(self, target_id: str, run_id: Optional[str] = None) -> List[ReplayRecord]:
        """Query replay logs matching targeted specifications."""
        filters = {"target_id": target_id}
        if run_id:
            filters["run_id"] = run_id
        return self.storage.list_replays(filters=filters)
