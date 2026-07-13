import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function main() {
  console.log("Starting Node.js intelligenceGateway verification...");

  try {
    const rawText = "We need to hire a DevOps engineer.";
    const source = "form";
    const senderEmail = "hr@client-company.com";
    const jobContext = {
      event_id: "evt_inquiry_abc",
      job_id: "job_inquiry_def",
      trace_id: "trace_inquiry_ghi"
    };

    console.log("Calling classifyCandidateIntent via Gateway...");
    const result = await intelligenceGateway.classifyCandidateIntent(rawText, source, senderEmail, jobContext);

    console.log("\n--- Gateway Returned Result ---");
    console.log(JSON.stringify(result, null, 2));

    // Assert correct classification
    if (result.intent === "client_inquiry") {
      console.log("\nSUCCESS: Gateway successfully routed and parsed client_inquiry intent!");
    } else {
      console.error("\nFAILURE: Intent did not match expected 'client_inquiry' classification.");
    }

  } catch (error) {
    console.error("Gateway verification failed with error:", error);
  } finally {
    await intelligenceGateway.close();
    console.log("Gateway verification finished.");
  }
}

main().catch(console.error);
