import { mcpClient } from "./mcpClient.js";

export const deploymentClient = {
  async bootstrap(manifest) {
    const raw = await mcpClient.callTool("deployment_bootstrap", {
      manifest
    });
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed deployment_bootstrap: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  async runDiagnostics() {
    const raw = await mcpClient.callTool("deployment_diagnostics", {});
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed deployment_diagnostics: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  async triggerRollback() {
    const raw = await mcpClient.callTool("deployment_rollback", {});
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed deployment_rollback: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  async listCapabilities() {
    const raw = await mcpClient.callTool("deployment_capabilities", {});
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed deployment_capabilities: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  }
};
