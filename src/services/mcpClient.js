import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import dotenv from "dotenv";
dotenv.config();

let clientInstance = null;
let transportInstance = null;

// Configurations loaded dynamically from environment
const pythonPath = process.env.PYTHON_PATH || "C:\\Users\\Nafiz\\Anaconda3\\envs\\pfolio_3.12.4\\python.exe";
const requestTimeoutMs = parseInt(process.env.MCP_REQUEST_TIMEOUT_MS || "10000", 10);

async function initClient() {
  if (clientInstance) return clientInstance;

  console.log(`[MCP Client] Initializing Stdio transport with Python executable: ${pythonPath}`);
  transportInstance = new StdioClientTransport({
    command: pythonPath,
    args: ["-m", "src.intelligence.mcp.server"]
  });

  clientInstance = new Client(
    {
      name: "meridian-automation-client",
      version: "1.0.0"
    },
    {
      capabilities: {}
    }
  );

  // Register cleanup callbacks on transport events
  transportInstance.onclose = () => {
    console.warn("[MCP Client] Stdio transport connection closed.");
    cleanup();
  };

  transportInstance.onerror = (err) => {
    console.error("[MCP Client] Stdio transport error:", err.message);
    cleanup();
  };

  await clientInstance.connect(transportInstance);
  console.log("[MCP Client] Handshake complete. Connected to MCP server.");
  return clientInstance;
}

function cleanup() {
  clientInstance = null;
  transportInstance = null;
}

export const mcpClient = {
  /**
   * Executes a generic tool call against the Python MCP server.
   * @param {string} toolName - Name of the registered MCP tool.
   * @param {Object} args - Arguments to pass.
   * @returns {Promise<string>} - The raw string result.
   */
  async callTool(toolName, args) {
    let client;
    try {
      client = await initClient();
    } catch (err) {
      console.error("[MCP Client] Failed to connect to server:", err.message);
      throw new Error(`MCP connection failed: ${err.message}`);
    }

    const timeout = requestTimeoutMs;
    let timeoutId;
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(() => {
        reject(new Error(`MCP Tool call timed out after ${timeout}ms`));
      }, timeout);
    });

    try {
      // Race the tool execution against the configurable timeout
      const response = await Promise.race([
        client.callTool({
          name: toolName,
          arguments: args
        }),
        timeoutPromise
      ]);
      clearTimeout(timeoutId);

      if (response && response.content && response.content[0] && response.content[0].type === "text") {
        if (response.isError) {
          throw new Error(response.content[0].text);
        }
        return response.content[0].text;
      }
      throw new Error("Invalid response format received from MCP tool");
    } catch (err) {
      clearTimeout(timeoutId);

      // Determine if error is a transport drop (requiring process restart) or domain error (ValidationError)
      const isTransportError =
        err.message.includes("EPIPE") ||
        err.message.includes("closed") ||
        err.message.includes("crashed") ||
        err.message.includes("Connection lost") ||
        err.message.includes("process exited") ||
        err.message.includes("timed out");

      if (isTransportError) {
        console.warn(`[MCP Client] Transport failure detected ("${err.message}"). Attempting to restart server and retry tool call...`);
        cleanup(); // Reset handles

        try {
          client = await initClient();
          const retryResponse = await client.callTool({
            name: toolName,
            arguments: args
          });
          if (retryResponse && retryResponse.content && retryResponse.content[0] && retryResponse.content[0].type === "text") {
            if (retryResponse.isError) {
              throw new Error(retryResponse.content[0].text);
            }
            return retryResponse.content[0].text;
          }
          throw new Error("Invalid response format received from MCP tool during retry");
        } catch (retryErr) {
          console.error("[MCP Client] Retry attempt failed:", retryErr.message);
          throw retryErr;
        }
      } else {
        // Business logic or validation error: propagate immediately without restarting
        throw err;
      }
    }
  },

  /**
   * Cleanly closes the transport channel.
   */
  async close() {
    if (transportInstance) {
      console.log("[MCP Client] Closing connection...");
      await transportInstance.close();
    }
    cleanup();
  }
};
