from .classifier import IntentClassifier


classifier = IntentClassifier()


async def classify_intent(input_data):

    return classifier.classify(
        input_data.raw_text
    )