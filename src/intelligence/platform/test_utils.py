import subprocess
import json

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
