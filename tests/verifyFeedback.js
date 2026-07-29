import fs from "fs";
import path from "path";
import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Human Feedback Platform...");

  let feedbackId = null;

  try {
    console.log("1. Submitting human rating feedback via gateway...");
    const submitRes = await intelligenceGateway.submitFeedback(
      "tool_nodejs_verify",
      "tool",
      "run_node_999",
      "rating",
      { score: 4.8 },
      "reviewer_node",
      "replay_node_123"
    );

    console.log("Submit Feedback Response:");
    console.log(JSON.stringify(submitRes, null, 2));

    if (submitRes.status !== "success" || !submitRes.feedback_record) {
      throw new Error("Invalid response when submitting feedback");
    }

    feedbackId = submitRes.feedback_record.feedback_id;
    console.log(`Successfully created feedback record: ${feedbackId}`);

    console.log("2. Querying feedback logs...");
    const listRes = await intelligenceGateway.listFeedback("tool_nodejs_verify");
    console.log("List Feedback Response:");
    console.log(JSON.stringify(listRes, null, 2));

    if (listRes.status !== "success" || !listRes.feedback_records || listRes.feedback_records.length === 0) {
      throw new Error("Invalid response or empty records list when listing feedback");
    }

    console.log("3. Computing target feedback summary...");
    const summaryRes = await intelligenceGateway.feedbackSummary("tool_nodejs_verify");
    console.log("Feedback Summary Response:");
    console.log(JSON.stringify(summaryRes, null, 2));

    if (summaryRes.status !== "success" || !summaryRes.analytics_summary) {
      throw new Error("Invalid analytics summary output");
    }

    console.log("4. Promoting reviewed replay to curated dataset...");
    const promoteRes = await intelligenceGateway.promoteDatasetItem(
      "replay_node_123",
      "intent",
      "curated",
      "v1",
      "node_admin"
    );
    console.log("Promote Dataset Item Response:");
    console.log(JSON.stringify(promoteRes, null, 2));

    if (promoteRes.status !== "success" || !promoteRes.promotion_request || promoteRes.promotion_request.status !== "approved") {
      throw new Error("Dataset item promotion did not return success approval status");
    }

    console.log("Node.js Human Feedback Platform E2E Verification PASSED successfully!");

  } catch (err) {
    console.error("Node.js E2E Verification FAILED:", err);
    process.exit(1);
  } finally {
    // Clean up created JSON records
    const feedbackDir = path.resolve("feedback");
    try {
      if (feedbackId && fs.existsSync(path.join(feedbackDir, "records", `${feedbackId}.json`))) {
        fs.unlinkSync(path.join(feedbackDir, "records", `${feedbackId}.json`));
      }
    } catch (e) {}
    await intelligenceGateway.close();
  }
}

run();
