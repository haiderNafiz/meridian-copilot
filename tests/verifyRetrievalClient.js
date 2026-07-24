import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function main() {
  console.log("Starting Node.js Knowledge Retrieval verification...");

  try {
    const query = "React frontend developer Cv architect";
    const collection = "default";
    const limit = 2;
    const threshold = 0.5;
    
    const jobContextData = {
      event_id: "evt_retrieval_e2e_1",
      job_id: "job_retrieval_e2e_1",
      trace_id: "trace_retrieval_e2e_1"
    };

    console.log("Calling retrieveKnowledge via Gateway...");
    const result = await intelligenceGateway.retrieveKnowledge(
      query,
      collection,
      limit,
      threshold,
      null, // filters
      jobContextData
    );

    console.log("\n--- Retrieval Gateway Returned Result ---");
    console.log(JSON.stringify(result, null, 2));

    const payload = result.payload;
    if (
      result.status === "success" &&
      result.metadata.provider === "mock_store" &&
      result.metadata.model === "mock-embed" &&
      Array.isArray(payload.results) &&
      payload.results.length >= 1 &&
      payload.results[0].text.includes("John is a frontend architect") &&
      payload.results[0].score === 1.0
    ) {
      console.log("\nSUCCESS: Knowledge retrieval executed, parsed, and validated successfully!");
    } else {
      console.error("\nFAILURE: Schema validation checks on Gateway result failed.");
    }

  } catch (error) {
    console.error("Knowledge retrieval verification failed with error:", error);
  } finally {
    await intelligenceGateway.close();
    console.log("Knowledge retrieval verification finished.");
  }
}

main().catch(console.error);
