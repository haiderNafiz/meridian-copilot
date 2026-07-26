import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Agent Orchestrator...");

  try {
    const sessionId = "session_node_orch_e2e_88";
    const queryText = "Larry is a senior Go architect with 8 years experience. He has AWS certification and is open to passive roles.";
    
    console.log("Triggering runOrchestration facade...");
    const res = await intelligenceGateway.runOrchestration(
      queryText,
      sessionId,
      null, // contextId
      [],   // forceTools
      "larry@example.com", // email
      "London, UK",       // location
      ["go", "aws"]       // technologyKeywords
    );

    console.log("Orchestration Success Response:");
    console.log(JSON.stringify(res, null, 2));

    // Validations
    if (res.status !== "success") {
      throw new Error(`Orchestration failed with status: ${res.status}`);
    }

    if (!res.execution_trace_id) {
      throw new Error("Missing execution_trace_id in response");
    }

    const completed = res.completed_steps || [];
    const requiredSteps = ["intent_classifier", "candidate_profiler", "deterministic_enricher", "knowledge_service", "qualification_scorer", "summarizer", "context_builder", "save_memory"];
    for (const step of requiredSteps) {
      if (!completed.includes(step)) {
        throw new Error(`Expected step '${step}' to be completed, but got steps: [${completed.join(", ")}]`);
      }
    }

    if (!res.context_snapshot) {
      throw new Error("Orchestration returned null context_snapshot");
    }

    const snapshot = res.context_snapshot;
    if (snapshot.facts.role_type !== "Backend") {
      throw new Error(`Expected role_type 'Backend', got '${snapshot.facts.role_type}'`);
    }

    console.log("Fetching saved memory snapshot to verify persistence log...");
    const memRes = await intelligenceGateway.retrieveMemory(null, snapshot.metadata.context_id, sessionId);
    console.log("Retrieved memory count:", memRes.memories.length);
    if (memRes.memories.length === 0) {
      throw new Error("No memory snapshots persisted during orchestration flow!");
    }

    console.log("\n>>> E2E Node.js Verification for Agent Orchestrator Passed Successfully! <<<\n");
  } catch (error) {
    console.error("E2E Verification Failed:", error);
    process.exit(1);
  } finally {
    await intelligenceGateway.close();
  }
}

run();
