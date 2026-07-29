import os
import json
from typing import Any, Dict, Optional
from .base import KnowledgeProvider
from ..schema import KnowledgeAsset

class LocalFilesystemKnowledgeProvider(KnowledgeProvider):
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../../../knowledge_platform")
            )
        else:
            self.base_dir = os.path.abspath(base_dir)

        self.assets_dir = os.path.join(self.base_dir, "assets")
        self.indices_dir = os.path.join(self.base_dir, "indices")

        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.indices_dir, exist_ok=True)

    def save_asset(self, asset: KnowledgeAsset) -> str:
        filepath = os.path.join(self.assets_dir, f"{asset.asset_id}_{asset.version}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(asset.model_dump_json(indent=2))
        return filepath

    def get_asset(self, asset_id: str, version: str) -> Optional[KnowledgeAsset]:
        filepath = os.path.join(self.assets_dir, f"{asset_id}_{version}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return KnowledgeAsset.model_validate(data)

    def save_index(self, index_name: str, index_data: Dict[str, Any]) -> str:
        filepath = os.path.join(self.indices_dir, f"{index_name}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        return filepath

    def load_index(self, index_name: str) -> Optional[Dict[str, Any]]:
        filepath = os.path.join(self.indices_dir, f"{index_name}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
