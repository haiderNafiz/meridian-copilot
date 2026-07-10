from .providers.rule_provider import RuleProvider

# Later:
# from .providers.groq_provider import GroqProvider


class IntentClassifier:

    def __init__(self):

        self.rule_provider = RuleProvider()

        # self.llm_provider = GroqProvider()

    def classify(self, text: str):

        # For now

        return self.rule_provider.classify(text)