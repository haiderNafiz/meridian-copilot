import json
import time
import sys
import uuid
from pydantic import ValidationError
from fastmcp import FastMCP
from src.intelligence.tools.intent_classifier.classifier import IntentClassifier
from src.intelligence.tools.intent_classifier.schema import IntentInput

# Create MCP server with name and version metadata
mcp = FastMCP("Meridian Intelligence Server", version="1.0.0")

def get_classifier() -> IntentClassifier:
    """
    Dependency injection factory to retrieve the Intent Classifier service instance.
    """
    return IntentClassifier()

@mcp.tool(
    name="classify_intent",
    description="Classify incoming candidate application, client inquiry, status check, or withdrawal message."
)
async def classify_intent(raw_text: str, source: str, sender_email: str, context: dict = None) -> str:
    """
    Classify the intent of the incoming message using the core IntentClassifier service.
    """
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    status = "success"
    provider = "unknown"
    fallback_used = False
    confidence = 0.0
    error_msg = None

    try:
        # Validate incoming transport payload parameters via Pydantic schema
        input_data = IntentInput(
            raw_text=raw_text,
            source=source,
            sender_email=sender_email
        )

        # Resolve classifier service instance
        classifier = get_classifier()

        # Delegate execution to the core classification business logic
        result = classifier.classify(input_data.raw_text)

        # Retrieve metrics for structured logging
        fallback_used = result.fallback_used
        confidence = result.confidence
        provider = "rules" if result.fallback_used else "groq"

        return result.model_dump_json()

    except ValidationError as val_err:
        status = "failure"
        error_msg = f"Validation Error: {str(val_err)}"
        raise val_err
    except Exception as exc:
        status = "failure"
        error_msg = f"Unexpected Error: {str(exc)}"
        raise exc
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Build clean structured log object
        log_payload = {
            "request_id": request_id,
            "tool_name": "classify_intent",
            "provider": provider,
            "fallback_used": fallback_used,
            "confidence": confidence,
            "duration_ms": round(duration_ms, 2),
            "status": status
        }
        if context:
            log_payload["event_id"] = context.get("event_id")
            log_payload["job_id"] = context.get("job_id")
            log_payload["trace_id"] = context.get("trace_id")
            
        if error_msg:
            log_payload["error"] = error_msg

        # Print JSON log to stderr to ensure stdio JSON-RPC remains clean on stdout
        print(json.dumps(log_payload), file=sys.stderr, flush=True)

if __name__ == "__main__":
    # Start the server using stdio transport
    mcp.run()
