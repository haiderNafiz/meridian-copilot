import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Planner Service...");

  try {
    const sessionId = "session_node_plan_e2e_88";
    const queryText = "Larry is a senior Go architect with 8 years experience. He has AWS certification and is open to passive roles.";

    console.log("1. Triggering runPlanner facade directly...");
    const planRes = await intelligenceGateway.runPlanner(
      queryText,
      sessionId,
      null, // contextId
      null, // forceWorkflow
      "larry@example.com", // email
      "London, UK", // location
      ["go", "aws"] // technologyKeywords
    );

    console.log("Planner Success Response:");
    console.log(JSON.stringify(planRes, null, 2));

    // Validations
    if (planRes.status !== "success") {
      throw new Error(`Planner failed with status: ${planRes.status}`);
    }

    if (planRes.selected_workflow !== "CandidateAssessmentWorkflow") {
      throw new Error(`Expected selected_workflow to be 'CandidateAssessmentWorkflow', got '${planRes.selected_workflow}'`);
    }

    if (!planRes.execution_plan || !Array.isArray(planRes.execution_plan.nodes)) {
      throw new Error("Missing execution_plan or nodes list");
    }

    console.log("2. Triggering runOrchestration facade (dynamically using Planner)...");
    const orchRes = await intelligenceGateway.runOrchestration(
      queryText,
      sessionId,
      null,
      [],
      "larry@example.com",
      "London, UK",
      ["go", "aws"]
    );

    console.log("Orchestration Success Response:");
    console.log(JSON.stringify(orchRes, null, 2));

    if (orchRes.status !== "success") {
      throw new Error(`Orchestration failed: ${orchRes.status}`);
    }

    console.log("Node.js Planner E2E Verification PASSED successfully!");
  } catch (err) {
    console.error("Node.js E2E Verification FAILED:", err);
    process.exit(1);
  } finally {
    await intelligenceGateway.close();
  }
}

run();
