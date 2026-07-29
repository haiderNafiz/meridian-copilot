import os
import json
from typing import Any, Dict, List, Optional
from .base import ReplayStorage
from ..schema import ReplayRecord

class LocalFilesystemStorage(ReplayStorage):
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../../replays")
            )
        else:
            self.base_dir = os.path.abspath(base_dir)
            
        os.makedirs(self.base_dir, exist_ok=True)

    def save_replay(self, replay: ReplayRecord) -> str:
        filepath = os.path.join(self.base_dir, f"{replay.replay_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(replay.model_dump_json(indent=2))
        return filepath

    def get_replay(self, replay_id: str) -> Optional[ReplayRecord]:
        filepath = os.path.join(self.base_dir, f"{replay_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ReplayRecord.model_validate(data)

    def list_replays(self, filters: Dict[str, Any] = None) -> List[ReplayRecord]:
        results = []
        if not os.path.exists(self.base_dir):
            return results
            
        for filename in os.listdir(self.base_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.base_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        record = ReplayRecord.model_validate(data)
                        
                        match = True
                        if filters:
                            for key, val in filters.items():
                                if getattr(record, key, None) != val:
                                    match = False
                                    break
                        if match:
                            results.append(record)
                except Exception:
                    continue
        return results
