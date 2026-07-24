import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function main() {
  console.log("Starting Node.js Candidate Summarizer verification...");

  try {
    const rawText = "Larry Page is a senior software engineer specialized in distributed systems and Go.";
    const jobDescriptionId = "doc_jd_go_dev";
    const email = "larry@google.com";
    const location = "Palo Alto, CA";
    const technologyKeywords = ["go", "distributed systems"];

    const jobContextData = {
      event_id: "evt_summarization_e2e_1",
      job_id: "job_summarization_e2e_1",
      trace_id: "trace_summarization_e2e_1"
    };

    console.log("Calling summarizeCandidate via Gateway...");
    const result = await intelligenceGateway.summarizeCandidate(
      rawText,
      jobDescriptionId,
      email,
      location,
      technologyKeywords,
      jobContextData
    );

    console.log("\n--- Summarizer Gateway Returned Result ---");
    console.log(JSON.stringify(result, null, 2));

    const payload = result.payload;
    if (
      result.status === "success" &&
      result.metadata.provider === "groq" &&
      result.metadata.model === "llama-3.3-70b-versatile" &&
      typeof payload === "object" &&
      typeof payload.executive_summary === "string" &&
      typeof payload.strengths === "object" &&
      Array.isArray(payload.strengths.evidence) &&
      typeof payload.strengths.reasoning === "string" &&
      typeof payload.weaknesses_or_risks === "object" &&
      Array.isArray(payload.weaknesses_or_risks.evidence) &&
      typeof payload.weaknesses_or_risks.reasoning === "string" &&
      typeof payload.recruiter_recommendation === "string" &&
      Array.isArray(payload.interview_focus) &&
      Array.isArray(payload.follow_up_questions) &&
      result.retrieved_chunks.includes("doc_jd_go_dev_chunk_0") &&
      result.provider_chain.includes("SummarizationProvider")
    ) {
      console.log("\nSUCCESS: Candidate summarization executed, parsed, and validated successfully!");
    } else {
      console.error("\nFAILURE: Schema validation checks on Gateway result failed.");
      process.exitCode = 1;
    }

  } catch (error) {
    console.error("Candidate summarization verification failed with error:", error);
    process.exitCode = 1;
  } finally {
    await intelligenceGateway.close();
    console.log("Candidate summarization verification finished.");
  }
}

main().catch(console.error);
