import { intelligenceGateway } from "../src/services/intelligenceGateway.js";
import assert from "assert";

async function main() {
  console.log("=== Starting Node.js E2E Monitoring Gateway Verification ===");
  try {
    const statusRes = await intelligenceGateway.monitoringStatus();
    console.log("Status Res:", JSON.stringify(statusRes, null, 2));
    assert.strictEqual(statusRes.status, "success");
    console.log("✓ Status check passed.");

    const healthRes = await intelligenceGateway.monitoringHealth("agent_verifier");
    console.log("Health Res:", JSON.stringify(healthRes, null, 2));
    assert.strictEqual(healthRes.status, "success");
    assert.strictEqual(healthRes.component.component_id, "agent_verifier");
    console.log("✓ Health verification passed.");

    const metricsRes = await intelligenceGateway.monitoringMetrics();
    console.log("Metrics Res:", JSON.stringify(metricsRes, null, 2));
    assert.strictEqual(metricsRes.status, "success");
    console.log("✓ Metrics query passed.");

    const eventsRes = await intelligenceGateway.monitoringEvents();
    console.log("Events Res:", JSON.stringify(eventsRes, null, 2));
    assert.strictEqual(eventsRes.status, "success");
    console.log("✓ Events query passed.");

    const alertsRes = await intelligenceGateway.monitoringAlerts();
    console.log("Alerts Res:", JSON.stringify(alertsRes, null, 2));
    assert.strictEqual(alertsRes.status, "success");
    console.log("✓ Alerts query passed.");

    console.log("=== E2E Monitoring Verification SUCCESS ===");
  } catch (error) {
    console.error("E2E Monitoring Verification FAILED:", error);
    process.exit(1);
  } finally {
    await intelligenceGateway.close();
  }
}

main();
