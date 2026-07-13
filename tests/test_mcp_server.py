import subprocess
import json
import os

def run_mcp_session(requests):
    """
    Helper function to spawn the MCP server as a subprocess, run the initialization handshake,
    send a list of request payloads, and return the stdout responses and all stderr output lines.
    """
    python_exe = r"C:\Users\Nafiz\Anaconda3\envs\pfolio_3.12.4\python.exe"
    
    proc = subprocess.Popen(
        [python_exe, "-m", "src.intelligence.mcp.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # 1. Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        proc.stdout.readline()  # read initialize response
        
        # 2. Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        proc.stdin.write(json.dumps(initialized_notif) + "\n")
        proc.stdin.flush()
        
        # 3. Send custom request payloads
        stdout_responses = []
        for req in requests:
            proc.stdin.write(json.dumps(req) + "\n")
            proc.stdin.flush()
            res = proc.stdout.readline().strip()
            stdout_responses.append(res)
            
    finally:
        # Terminate process and read stderr
        proc.terminate()
        stdout_rem, stderr_rem = proc.communicate()
        
    stderr_lines = stderr_rem.splitlines()
    return stdout_responses, stderr_lines

def test_mcp_tool_success_logs():
    # Call classify_intent with valid arguments
    call_req = {
        "jsonrpc": "2.0",
        "id": 101,
        "method": "tools/call",
        "params": {
            "name": "classify_intent",
            "arguments": {
                "raw_text": "Attached is my resume for the engineering role.",
                "source": "email",
                "sender_email": "mei@outlook.com"
            }
        }
    }
    
    responses, stderr_lines = run_mcp_session([call_req])
    
    # Ensure stdout returned a valid response
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "error" not in resp
    assert "result" in resp
    assert resp["result"].get("isError", False) is False
    
    # Extract our structured JSON logs from stderr
    json_logs = []
    for line in stderr_lines:
        try:
            parsed = json.loads(line)
            if "request_id" in parsed:
                json_logs.append(parsed)
        except json.JSONDecodeError:
            continue
            
    assert len(json_logs) == 1
    success_log = json_logs[0]
    
    # Validate log payload contains correct execution tracking metadata
    assert success_log["tool_name"] == "classify_intent"
    assert success_log["status"] == "success"
    assert success_log["provider"] == "rules"
    assert success_log["fallback_used"] is True
    assert success_log["confidence"] == 0.8
    assert "request_id" in success_log
    assert "duration_ms" in success_log
    assert isinstance(success_log["duration_ms"], float)

def test_mcp_tool_failure_logs():
    # Call classify_intent with an invalid email parameter to trigger ValidationError
    call_req = {
        "jsonrpc": "2.0",
        "id": 102,
        "method": "tools/call",
        "params": {
            "name": "classify_intent",
            "arguments": {
                "raw_text": "Hello, hiring team",
                "source": "email",
                "sender_email": "not-a-valid-email-format"
            }
        }
    }
    
    responses, stderr_lines = run_mcp_session([call_req])
    
    # Ensure stdout returned a response indicating an error
    assert len(responses) == 1
    resp = json.loads(responses[0])
    assert "result" in resp
    assert resp["result"].get("isError") is True
    
    # Extract our structured JSON logs from stderr
    json_logs = []
    for line in stderr_lines:
        try:
            parsed = json.loads(line)
            if "request_id" in parsed:
                json_logs.append(parsed)
        except json.JSONDecodeError:
            continue
            
    assert len(json_logs) == 1
    failure_log = json_logs[0]
    
    # Validate log payload captures the validation failure and traceback details
    assert failure_log["tool_name"] == "classify_intent"
    assert failure_log["status"] == "failure"
    assert "error" in failure_log
    assert "Validation Error" in failure_log["error"]
    assert "request_id" in failure_log
    assert "duration_ms" in failure_log
