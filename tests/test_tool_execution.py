#!/usr/bin/env python3
import json
import subprocess
import sys

def test_tool_execution():
    """Test executing a MongoDB tool to see lazy connection in action"""
    
    process = subprocess.Popen(
        ['python3', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Initialize
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(initialize_request) + '\n')
        process.stdin.flush()
        response = process.stdout.readline()
        print("✓ Server initialized\n")
        
        # Test MongoDB tool (this should work with your atlas_mongo)
        print("Testing find_mongodb with 'atlas_mongo':")
        print("-" * 50)
        find_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "find_mongodb",
                "arguments": {
                    "db_id": "atlas_mongo",
                    "collection": "test",
                    "query": "{}"
                }
            }
        }
        
        process.stdin.write(json.dumps(find_request) + '\n')
        process.stdin.flush()
        response = process.stdout.readline()
        result = json.loads(response)
        
        if "result" in result:
            print("✓ SUCCESS - Connected to MongoDB!")
            print(f"Result: {json.dumps(result['result'], indent=2)}")
        elif "error" in result:
            print("✗ ERROR:")
            print(json.dumps(result['error'], indent=2))
        
        print("\n" + "=" * 50 + "\n")
        
        # Test PostgreSQL tool (this should fail - no credentials)
        print("Testing query_postgres with 'prod_postgres' (no credentials):")
        print("-" * 50)
        pg_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "query_postgres",
                "arguments": {
                    "db_id": "prod_postgres",
                    "query": "SELECT 1"
                }
            }
        }
        
        process.stdin.write(json.dumps(pg_request) + '\n')
        process.stdin.flush()
        response = process.stdout.readline()
        result = json.loads(response)
        
        if "result" in result:
            print("✓ SUCCESS:")
            print(json.dumps(result['result'], indent=2))
        elif "error" in result:
            print("✗ EXPECTED ERROR (no credentials configured):")
            print(f"Message: {result['error'].get('message', 'Unknown error')}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        process.terminate()
        process.wait(timeout=2)

if __name__ == "__main__":
    test_tool_execution()
