import { mcpClient } from "../src/services/mcpClient.js";

async function main() {
  console.log("Starting Node.js mcpClient verification...");

  try {
    const rawText = "Attached is my CV. I would like to apply for the Backend position.";
    const source = "email";
    const senderEmail = "mei@outlook.com";
    const context = {
      event_id: "evt_test_123",
      job_id: "job_test_456",
      trace_id: "trace_test_789"
    };

    console.log("Calling classify_intent via mcpClient...");
    const result = await mcpClient.callTool("classify_intent", {
      raw_text: rawText,
      source: source,
      sender_email: senderEmail,
      context: context
    });

    console.log("\n--- Successful Tool Call Result ---");
    console.log(result);

    // Verify error routing with invalid input
    console.log("\nCalling with invalid inputs to verify validation error handling...");
    try {
      await mcpClient.callTool("classify_intent", {
        raw_text: rawText,
        source: "invalid_source_literal",
        sender_email: "not-an-email"
      });
      console.error("ERROR: Expected call to fail, but it succeeded.");
    } catch (valErr) {
      console.log("\n--- Propagated Validation Error ---");
      console.log(valErr.message);
    }

  } catch (error) {
    console.error("Verification failed with error:", error);
  } finally {
    await mcpClient.close();
    console.log("\nVerification finished.");
  }
}

main().catch(console.error);
