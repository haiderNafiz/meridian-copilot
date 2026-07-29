from typing import Dict, Optional, Callable, List, Any
from .definition import MetricDefinition

class MetricRegistry:
    def __init__(self):
        self._metrics: Dict[str, MetricDefinition] = {}
        self._strategy_factories: Dict[str, Callable] = {}

    def register_metric(self, definition: MetricDefinition, factory_func: Callable):
        """Register a new metric definition and strategy factory."""
        self._metrics[definition.name] = definition
        self._strategy_factories[definition.name] = factory_func

    def get_definition(self, name: str) -> Optional[MetricDefinition]:
        return self._metrics.get(name)

    def create_strategy(self, name: str) -> Optional[Any]:
        factory = self._strategy_factories.get(name)
        if factory:
            return factory()
        return None

    def list_registered_metrics(self) -> List[MetricDefinition]:
        return list(self._metrics.values())

_registry_instance = None

def get_metric_registry() -> MetricRegistry:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = MetricRegistry()
    return _registry_instance
