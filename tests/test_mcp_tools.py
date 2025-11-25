#!/usr/bin/env python3
import json
import subprocess
import sys

def test_mcp_server():
    process = subprocess.Popen(
        ['python3', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(initialize_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            print("Initialize Response:")
            print(json.dumps(json.loads(response_line), indent=2))
            print()
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print("Available MCP Tools:")
            print("=" * 50)
            
            if "result" in response and "tools" in response["result"]:
                for tool in response["result"]["tools"]:
                    print(f"\n{tool['name']}")
                    print(f"  {tool.get('description', 'No description')}")
                    if 'inputSchema' in tool:
                        props = tool['inputSchema'].get('properties', {})
                        if props:
                            print(f"  Parameters:")
                            for param_name, param_info in props.items():
                                param_type = param_info.get('type', 'any')
                                param_desc = param_info.get('description', '')
                                print(f"    - {param_name} ({param_type}): {param_desc}")
            else:
                print("No tools found or error in response:")
                print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        stderr = process.stderr.read()
        if stderr:
            print(f"Server stderr: {stderr}", file=sys.stderr)
    finally:
        process.terminate()
        process.wait(timeout=2)

if __name__ == "__main__":
    test_mcp_server()
