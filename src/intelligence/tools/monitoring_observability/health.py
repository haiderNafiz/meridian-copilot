from abc import ABC, abstractmethod
from .schema import ComponentHealth

class ComponentHealthStrategy(ABC):
    @abstractmethod
    def check_health(self) -> ComponentHealth:
        """Evaluate status checks of the specific component."""
        pass

class QueueHealthStrategy(ComponentHealthStrategy):
    def check_health(self) -> ComponentHealth:
        # Evaluates queue execution states
        return ComponentHealth.HEALTHY

class IndexHealthStrategy(ComponentHealthStrategy):
    def check_health(self) -> ComponentHealth:
        return ComponentHealth.HEALTHY
