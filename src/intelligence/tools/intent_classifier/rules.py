from .schema import IntentOutput


def classify_with_rules(text: str) -> IntentOutput:

    text = text.lower()

    if "withdraw" in text:
        return IntentOutput(
            intent="withdrawal",
            confidence=0.9,
            fallback_used=True,
            reasoning="Withdrawal keyword detected"
        )

    if "resume" in text:
        return IntentOutput(
            intent="new_candidate_application",
            confidence=0.8,
            fallback_used=True,
            reasoning="Resume keyword detected"
        )

    if "cv" in text:
        return IntentOutput(
            intent="new_candidate_application",
            confidence=0.8,
            fallback_used=True,
            reasoning="CV keyword detected"
        )

    if "hire" in text:
        return IntentOutput(
            intent="client_inquiry",
            confidence=0.8,
            fallback_used=True,
            reasoning="Hiring keyword detected"
        )

    if "application status" in text:
        return IntentOutput(
            intent="status_check",
            confidence=0.8,
            fallback_used=True,
            reasoning="Status keyword detected"
        )

    return IntentOutput(
        intent="unknown",
        confidence=0.3,
        fallback_used=True,
        reasoning="No matching rules"
    )