import { mcpClient } from "./mcpClient.js";

export const monitoringClient = {
  async monitoringStatus(componentId = null) {
    const raw = await mcpClient.callTool("monitoring_status", {
      component_id: componentId
    });
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed monitoring_status: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  async monitoringMetrics(category = null) {
    const raw = await mcpClient.callTool("monitoring_metrics", {
      category
    });
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed monitoring_metrics: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  async monitoringEvents(severity = null) {
    const raw = await mcpClient.callTool("monitoring_events", {
      severity
    });
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed monitoring_events: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  async monitoringHealth(componentId) {
    const raw = await mcpClient.callTool("monitoring_health", {
      component_id: componentId
    });
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed monitoring_health: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  async monitoringAlerts() {
    const raw = await mcpClient.callTool("monitoring_alerts", {});
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed monitoring_alerts: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  async monitoringTrace(traceId) {
    const raw = await mcpClient.callTool("monitoring_trace", {
      trace_id: traceId
    });
    const parsed = JSON.parse(raw);
    if (parsed.status !== "success") {
      throw new Error(`Failed monitoring_trace: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  }
};
