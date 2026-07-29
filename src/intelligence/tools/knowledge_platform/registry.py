from typing import Dict, List, Optional, Any
from .schema import KnowledgeAsset

class KnowledgeRegistry:
    def __init__(self):
        self._assets: Dict[str, Dict[str, KnowledgeAsset]] = {}
        self._namespaces: Dict[str, List[str]] = {}

    def register_asset(self, asset: KnowledgeAsset) -> None:
        if asset.asset_id not in self._assets:
            self._assets[asset.asset_id] = {}
        self._assets[asset.asset_id][asset.version] = asset

        if asset.namespace not in self._namespaces:
            self._namespaces[asset.namespace] = []
        if asset.asset_id not in self._namespaces[asset.namespace]:
            self._namespaces[asset.namespace].append(asset.asset_id)

    def get_asset(self, asset_id: str, version: str = "latest") -> Optional[KnowledgeAsset]:
        if asset_id not in self._assets:
            return None
        versions = self._assets[asset_id]
        if version == "latest":
            sorted_versions = sorted(versions.keys())
            return versions[sorted_versions[-1]] if sorted_versions else None
        return versions.get(version)

    def get_lineage(self, asset_id: str) -> List[KnowledgeAsset]:
        """Return the version history lineage of an asset from earliest to latest."""
        if asset_id not in self._assets:
            return []
        versions = self._assets[asset_id]
        sorted_versions = sorted(versions.keys())
        return [versions[v] for v in sorted_versions]

    def list_assets_in_namespace(self, namespace: str) -> List[KnowledgeAsset]:
        asset_ids = self._namespaces.get(namespace, [])
        results = []
        for aid in asset_ids:
            asset = self.get_asset(aid, version="latest")
            if asset:
                results.append(asset)
        return results

    def list_namespaces(self) -> List[str]:
        return list(self._namespaces.keys())
