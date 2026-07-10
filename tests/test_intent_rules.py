from src.intelligence.tools.intent_classifier.rules import (
    classify_with_rules
)


def test_application():

    result = classify_with_rules(
        "Attached is my resume"
    )

    assert result.intent == \
        "new_candidate_application"


def test_client():

    result = classify_with_rules(
        "We need to hire a DevOps Lead"
    )

    assert result.intent == \
        "client_inquiry"