import fs from "fs";
import path from "path";
import { intelligenceGateway } from "../src/services/intelligenceGateway.js";
import assert from "assert";

async function main() {
  console.log("=== Starting Node.js E2E Deployment Gateway Verification ===");
  
  const baseDir = path.resolve("deployment_platform");
  fs.mkdirSync(baseDir, { recursive: true });
  const profile = {
    profile_id: "prof_e2e",
    environment: "production",
    release_channel: "stable",
    version: "v1.0.0",
    feature_flags: [],
    parameters: {}
  };
  fs.writeFileSync(path.join(baseDir, "profiles.jsonl"), JSON.stringify(profile) + "\n");
  
  try {
    const manifest = {
      manifest_id: "man_e2e",
      profile_id: "prof_e2e",
      platform_version: "1.0.0",
      created_at: "2026-07-30",
      created_by: "e2e_tester",
      checksum: "sha256_e2e",
      plugins: [
        {
          plugin_name: "retrieval_plugin",
          version: "1.0.0",
          entry_point: "RetrievalPluginClass",
          dependencies: [
            { dependency_id: "knowledge_platform", dependency_type: "module", required_version: ">=2.0" }
          ],
          capabilities: ["e2e_capability"]
        }
      ]
    };

    const bootRes = await intelligenceGateway.deploymentBootstrap(manifest);
    console.log("Bootstrap Response:", JSON.stringify(bootRes, null, 2));
    assert.strictEqual(bootRes.status, "success");
    assert.strictEqual(bootRes.diagnostics.system_state, "ready");
    console.log("✓ System bootstrapped successfully.");

    const capRes = await intelligenceGateway.deploymentCapabilities();
    console.log("Capabilities Response:", JSON.stringify(capRes, null, 2));
    assert.ok(capRes.message.includes("e2e_capability"));
    console.log("✓ Capability registration verified.");

    const diagRes = await intelligenceGateway.deploymentDiagnostics();
    console.log("Diagnostics Response:", JSON.stringify(diagRes, null, 2));
    assert.strictEqual(diagRes.status, "success");
    console.log("✓ Diagnostics retrieval passed.");

    const rollbackRes = await intelligenceGateway.deploymentRollback();
    console.log("Rollback Response:", JSON.stringify(rollbackRes, null, 2));
    assert.strictEqual(rollbackRes.status, "success");
    console.log("✓ Rollback triggered successfully.");

    console.log("=== E2E Deployment Verification SUCCESS ===");
  } catch (error) {
    console.error("E2E Deployment Verification FAILED:", error);
    process.exit(1);
  } finally {
    try {
      if (fs.existsSync(path.join(baseDir, "profiles.jsonl"))) {
        fs.unlinkSync(path.join(baseDir, "profiles.jsonl"));
      }
      if (fs.existsSync(path.join(baseDir, "manifests.jsonl"))) {
        fs.unlinkSync(path.join(baseDir, "manifests.jsonl"));
      }
      fs.rmdirSync(baseDir);
    } catch (e) {}
    await intelligenceGateway.close();
  }
}

main();
