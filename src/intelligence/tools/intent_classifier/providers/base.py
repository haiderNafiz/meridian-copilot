from abc import ABC, abstractmethod

from ..schema import IntentOutput


class IntentProvider(ABC):

    @abstractmethod
    def classify(self, text: str) -> IntentOutput:
        """
        Classify the intent of the given text.
        """
        pass