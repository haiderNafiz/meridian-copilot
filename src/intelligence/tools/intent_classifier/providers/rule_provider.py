from .base import IntentProvider

from ..rules import classify_with_rules

from ..schema import IntentOutput


class RuleProvider(IntentProvider):

    def classify(self, text: str) -> IntentOutput:

        return classify_with_rules(text)