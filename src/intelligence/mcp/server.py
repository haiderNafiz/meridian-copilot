from fastmcp import FastMCP

# Create MCP server with name and version metadata
mcp = FastMCP("Meridian Intelligence Server", version="1.0.0")

@mcp.tool(
    name="classify_intent",
    description="Classify incoming candidate application, client inquiry, status check, or withdrawal message."
)
async def classify_intent(raw_text: str, source: str, sender_email: str) -> str:
    """
    Placeholder classification tool.
    Returns a placeholder JSON string conforming to the IntentOutput schema.
    """
    # Placeholder response matching IntentOutput schema
    return '{"intent": "unknown", "confidence": 0.0, "fallback_used": true, "reasoning": "Placeholder classification"}'

if __name__ == "__main__":
    # Start the server using stdio transport
    mcp.run()
