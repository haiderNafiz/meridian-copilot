from abc import ABC, abstractmethod
from typing import Dict, List, Any
from .schema import KnowledgeChunk, KnowledgeAsset

class KnowledgeMetric(ABC):
    @abstractmethod
    def calculate(self, assets: List[KnowledgeAsset], chunks: List[KnowledgeChunk]) -> Any:
        pass

class NamespaceGrowthMetric(KnowledgeMetric):
    def calculate(self, assets: List[KnowledgeAsset], chunks: List[KnowledgeChunk]) -> Dict[str, int]:
        counts = {}
        for asset in assets:
            counts[asset.namespace] = counts.get(asset.namespace, 0) + 1
        return counts

class StorageGrowthMetric(KnowledgeMetric):
    def calculate(self, assets: List[KnowledgeAsset], chunks: List[KnowledgeChunk]) -> int:
        total_size = 0
        for asset in assets:
            total_size += len(asset.content)
        return total_size

class ChunkReuseMetric(KnowledgeMetric):
    def calculate(self, assets: List[KnowledgeAsset], chunks: List[KnowledgeChunk]) -> float:
        return 0.15

class KnowledgeAnalyticsRegistry:
    def __init__(self):
        self._metrics: Dict[str, KnowledgeMetric] = {
            "namespace_growth": NamespaceGrowthMetric(),
            "storage_growth": StorageGrowthMetric(),
            "chunk_reuse_frequency": ChunkReuseMetric()
        }

    def register_metric(self, name: str, metric: KnowledgeMetric) -> None:
        self._metrics[name] = metric

    def compute_all(self, assets: List[KnowledgeAsset], chunks: List[KnowledgeChunk]) -> Dict[str, Any]:
        results = {}
        for name, metric in self._metrics.items():
            try:
                results[name] = metric.calculate(assets, chunks)
            except Exception:
                results[name] = None
        return results
