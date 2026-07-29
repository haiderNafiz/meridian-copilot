import fs from "fs";
import path from "path";
import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Replay & Debug Framework...");

  let replayId = null;

  try {
    console.log("1. Creating a manual replay via intelligence gateway...");
    const createRes = await intelligenceGateway.createReplay(
      "evaluation_default",
      { text: "hello math" },
      { value: "reproduced_output", confidence: 0.95 },
      "parent_root_123"
    );

    console.log("Create Replay Gateway Response:");
    console.log(JSON.stringify(createRes, null, 2));

    if (createRes.status !== "success" || !createRes.replay_record) {
      throw new Error("Invalid response format when creating replay");
    }

    replayId = createRes.replay_record.replay_id;
    console.log(`Successfully created replay with ID: ${replayId}`);

    console.log("2. Running exact replay execution...");
    const execRes = await intelligenceGateway.replayExecution(replayId);
    console.log("Replay Execution Gateway Response:");
    console.log(JSON.stringify(execRes, null, 2));

    if (execRes.status !== "success" || !execRes.execution_result) {
      throw new Error("Invalid response format when executing replay");
    }

    console.log("3. Comparing executions...");
    const diffRes = await intelligenceGateway.compareReplays(replayId);
    console.log("Compare Replays Gateway Response:");
    console.log(JSON.stringify(diffRes, null, 2));

    if (diffRes.status !== "success" || !diffRes.diff) {
      throw new Error("Invalid response format when comparing replays");
    }

    console.log("4. Generating Debug Report (Markdown format)...");
    const reportRes = await intelligenceGateway.generateDebugReport(replayId, null, "markdown");
    console.log("Debug Report Path:", reportRes.report_path);

    if (reportRes.status !== "success" || !reportRes.report_path) {
      throw new Error("Invalid response format when generating debug report");
    }

    if (!fs.existsSync(reportRes.report_path)) {
      throw new Error(`Report file does not exist at path: ${reportRes.report_path}`);
    }

    console.log("Node.js Replay & Debug Framework E2E Verification PASSED successfully!");

    // Cleanup generated report
    try {
      fs.unlinkSync(reportRes.report_path);
    } catch (e) {}

  } catch (err) {
    console.error("Node.js E2E Verification FAILED:", err);
    process.exit(1);
  } finally {
    // Cleanup generated replay json log
    if (replayId) {
      const replaysDir = path.resolve("replays");
      const replayPath = path.join(replaysDir, `${replayId}.json`);
      try {
        if (fs.existsSync(replayPath)) {
          fs.unlinkSync(replayPath);
        }
      } catch (e) {}
    }
    await intelligenceGateway.close();
  }
}

run();
