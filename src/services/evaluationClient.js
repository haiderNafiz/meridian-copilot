import { mcpClient } from "./mcpClient.js";

export const evaluationClient = {
  /**
   * Run evaluation on a dataset using target component configuration settings.
   * @param {string} domain - The dataset domain (e.g. "intent").
   * @param {string} datasetType - The dataset type (e.g. "golden").
   * @param {string} version - The version of the dataset (e.g. "v1").
   * @param {Object} config - Mapped metric targets.
   * @param {string} [experimentId] - Optional experiment identification tag.
   * @param {Object} [context] - Tracing context metrics.
   * @returns {Promise<Object>} The compiled evaluation report.
   */
  async runEvaluation(domain, datasetType, version, config, experimentId = "exp_default", context = {}) {
    const rawResult = await mcpClient.callTool("run_evaluation", {
      domain,
      dataset_type: datasetType,
      version,
      config,
      experiment_id: experimentId,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string" || !parsed.report) {
      throw new Error("Invalid domain schema structure returned from run_evaluation tool");
    }
    return parsed;
  }
};
