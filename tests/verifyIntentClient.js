import { intentClient } from "../src/services/intentClient.js";
import { mcpClient } from "../src/services/mcpClient.js";

async function main() {
  console.log("Starting Node.js intentClient verification...");

  try {
    const rawText = "I want to withdraw my application.";
    const source = "form";
    const senderEmail = "applicant@example.com";
    const context = {
      event_id: "evt_withdraw_999",
      job_id: "job_withdraw_888",
      trace_id: "trace_withdraw_777"
    };

    console.log("Calling classifyCandidateIntent...");
    const result = await intentClient.classifyCandidateIntent(rawText, source, senderEmail, context);

    console.log("\n--- Parsed IntentClient Domain Result ---");
    console.log("Type of result:", typeof result);
    console.log(JSON.stringify(result, null, 2));

    // Assert correct mapping
    if (result.intent === "withdrawal" && result.confidence === 0.9) {
      console.log("\nSUCCESS: Intent and confidence correctly parsed!");
    } else {
      console.error("\nFAILURE: Intent properties did not match expected values.");
    }

  } catch (error) {
    console.error("Verification failed with error:", error);
  } finally {
    await mcpClient.close();
    console.log("Verification finished.");
  }
}

main().catch(console.error);
