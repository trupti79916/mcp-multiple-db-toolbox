#!/usr/bin/env python3
"""Test MCP server startup to diagnose connection issues"""
import sys
import os

# Set environment variable for testing
os.environ['MONGODB_ATLAS_URI'] = 'mongodb+srv://2024sl93104_db_user:ryLb8mtNcmxCD7c1@nozama-data.q14xknz.mongodb.net/?appName=nozama-data'

print("=== MCP Server Startup Test ===", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Working directory: {os.getcwd()}", file=sys.stderr)

try:
    print("1. Loading config...", file=sys.stderr)
    from config_parser import load_config
    configs = load_config()
    print(f"   ✓ Loaded {len(configs)} database(s)", file=sys.stderr)
    
    print("2. Importing FastMCP...", file=sys.stderr)
    from mcp.server.fastmcp import FastMCP
    print("   ✓ FastMCP imported", file=sys.stderr)
    
    print("3. Initializing MCP server...", file=sys.stderr)
    mcp = FastMCP("multi-db-toolbox")
    print("   ✓ MCP server initialized", file=sys.stderr)
    
    print("4. Defining tools...", file=sys.stderr)
    
    @mcp.tool()
    def test_tool() -> str:
        """A simple test tool"""
        return "Hello from MCP!"
    
    print("   ✓ Tools defined", file=sys.stderr)
    
    print("5. Starting server with stdio transport...", file=sys.stderr)
    mcp.run(transport="stdio")
    
except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
