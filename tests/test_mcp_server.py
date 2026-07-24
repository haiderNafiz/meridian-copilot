import subprocess
import json
import os
from src.intelligence.platform.test_utils import run_mcp_session

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
