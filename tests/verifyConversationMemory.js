import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Conversation Memory...");

  try {
    const sessionId = "session_node_conv_e2e_88";
    
    console.log("1. Posting a user conversation turn containing contact and tasks...");
    const postRes = await intelligenceGateway.postConversationTurn(
      sessionId,
      "user",
      "Is Larry available for a quick call? Please email him at larry@example.com. Action: draft email.",
      "assess_candidate"
    );

    console.log("Post Turn Success Response:");
    console.log(JSON.stringify(postRes, null, 2));

    if (postRes.status !== "success") {
      throw new Error(`Expected status 'success', got '${postRes.status}'`);
    }

    console.log("2. Retrieving consolidated session conversation context...");
    const contextRes = await intelligenceGateway.getConversationContext(sessionId);

    console.log("Retrieve Context Success Response:");
    console.log(JSON.stringify(contextRes, null, 2));

    // Validation checks
    const context = contextRes.context;
    if (!context) {
      throw new Error("Context field is missing in context retrieve response");
    }

    if (context.active_goal !== "assess_candidate") {
      throw new Error(`Expected active_goal 'assess_candidate', got '${context.active_goal}'`);
    }

    if (!context.active_entities.email || context.active_entities.email !== "larry@example.com") {
      throw new Error("Missing or invalid email in active_entities");
    }

    if (!context.unresolved_questions.includes("Is Larry available for a quick call?")) {
      throw new Error("Missing question in unresolved_questions");
    }

    if (!context.pending_actions.includes("Action: draft email.")) {
      throw new Error("Missing action in pending_actions");
    }

    console.log("Node.js Conversation Memory E2E Verification PASSED successfully!");
  } catch (err) {
    console.error("Node.js E2E Verification FAILED:", err);
    process.exit(1);
  } finally {
    await intelligenceGateway.close();
  }
}

run();
