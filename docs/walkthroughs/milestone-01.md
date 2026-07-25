# Milestone 1 — Stdio Gateway & Base Infrastructure

## 1. Overview
Establishes the foundational split-process architecture connecting the Node.js API client and the Python intelligence server using standard I/O (stdio) transport.

## 2. Key Components
- **`mcpClient.js`**: Spawns python executable subprocess and manages stdio JSON-RPC streams.
- **`contracts.py`**: BaseRequest and BaseResponse contracts.
- **`config.py`**: Auto-dotenv loader.
- **`telemetry.py`**: Stderr-directed logging utility.
