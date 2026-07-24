import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function main() {
  console.log("Starting Node.js Candidate Profiler verification...");

  try {
    const rawText = "Mei is a backend developer with 10 years of experience building distributed systems, REST APIs, and automating pipelines using Docker. She is looking for an immediate change.";
    const currentTitle = "Backend Engineer";
    const skills = ["REST APIs", "Docker", "Go", "Python"];
    const yearsExperience = 10;
    const jobContext = {
      role_requirements: "Backend Engineer with Docker and Go experience."
    };
    const jobContextData = {
      event_id: "evt_profiler_e2e_1",
      job_id: "job_profiler_e2e_1",
      trace_id: "trace_profiler_e2e_1"
    };

    console.log("Calling profileCandidate via Gateway...");
    const result = await intelligenceGateway.profileCandidate(
      rawText,
      currentTitle,
      skills,
      yearsExperience,
      jobContext,
      jobContextData
    );

    console.log("\n--- Profiler Gateway Returned Result ---");
    console.log(JSON.stringify(result, null, 2));

    // Verify properties
    if (
      typeof result.role_type === "string" &&
      typeof result.seniority === "string" &&
      typeof result.urgency === "string" &&
      typeof result.open_to_negotiation === "boolean" &&
      Array.isArray(result.predicted_functions) &&
      Array.isArray(result.technical_domains) &&
      (result.management_level === null || typeof result.management_level === "string") &&
      Array.isArray(result.evidence) &&
      typeof result.confidence === "number" &&
      typeof result.reasoning === "string"
    ) {
      console.log("\nSUCCESS: Candidate profiling executed, parsed, and validated successfully!");
    } else {
      console.error("\nFAILURE: Schema validation checks on Gateway result failed.");
    }

  } catch (error) {
    console.error("Candidate profiler verification failed with error:", error);
  } finally {
    await intelligenceGateway.close();
    console.log("Candidate profiler verification finished.");
  }
}

main().catch(console.error);
