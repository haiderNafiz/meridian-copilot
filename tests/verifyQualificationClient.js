import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function main() {
  console.log("Starting Node.js Qualification Scorer verification...");

  try {
    const rawText = "Larry Page is a senior software engineer specialized in distributed systems and Go.";
    const jobDescriptionId = "doc_jd_go_dev";
    const email = "larry@google.com";
    const location = "Palo Alto, CA";
    const technologyKeywords = ["go", "distributed systems"];

    const jobContextData = {
      event_id: "evt_qualification_e2e_1",
      job_id: "job_qualification_e2e_1",
      trace_id: "trace_qualification_e2e_1"
    };

    console.log("Calling scoreQualification via Gateway...");
    const result = await intelligenceGateway.scoreQualification(
      rawText,
      jobDescriptionId,
      email,
      location,
      technologyKeywords,
      jobContextData
    );

    console.log("\n--- Qualification Gateway Returned Result ---");
    console.log(JSON.stringify(result, null, 2));

    const payload = result.payload;
    if (
      result.status === "success" &&
      result.metadata.provider === "groq" &&
      result.metadata.model === "llama-3.3-70b-versatile" &&
      typeof payload.scores === "object" &&
      typeof payload.reconciliation_notes === "string" &&
      Array.isArray(result.retrieved_chunks) &&
      result.retrieved_chunks.includes("doc_jd_go_dev_chunk_0")
    ) {
      console.log("\nSUCCESS: Qualification scoring executed, parsed, and validated successfully!");
    } else {
      console.error("\nFAILURE: Schema validation checks on Gateway result failed.");
      process.exitCode = 1;
    }

  } catch (error) {
    console.error("Qualification scoring verification failed with error:", error);
    process.exitCode = 1;
  } finally {
    await intelligenceGateway.close();
    console.log("Qualification scoring verification finished.");
  }
}

main().catch(console.error);
