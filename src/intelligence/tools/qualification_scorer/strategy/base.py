from abc import ABC, abstractmethod
from ..schema import QualificationInput, QualificationOutput

class QualificationStrategy(ABC):
    @abstractmethod
    def qualify(self, request: QualificationInput) -> QualificationOutput:
        """Execute qualification evaluation matching the configured strategy."""
        pass
