#!/usr/bin/env python3
"""
Test MCP Server Standalone

This script tests if the Stock MCP server can start and initialize properly.
Run this BEFORE testing the full integration.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

print()
print("=" * 80)
print("🧪 MCP SERVER STANDALONE TEST")
print("=" * 80)
print()

server_path = "tradingagents/mcp_servers/stock_server/server.py"

print(f"Testing server: {server_path}")
print()

# Test 1: Check if file exists
print("-" * 80)
print("TEST 1: Check if server file exists")
print("-" * 80)
if os.path.exists(server_path):
    print(f"✅ File exists: {server_path}")
else:
    print(f"❌ File not found: {server_path}")
    exit(1)
print()

# Test 2: Try to import the server
print("-" * 80)
print("TEST 2: Try to import server module")
print("-" * 80)
try:
    sys.path.insert(0, os.getcwd())
    from tradingagents.mcp_servers.stock_server import server as server_module
    print("✅ Server module imports successfully")
    print(f"   Server app: {server_module.app}")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
print()

# Test 3: Check MCP dependencies
print("-" * 80)
print("TEST 3: Check MCP dependencies")
print("-" * 80)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    print("✅ MCP packages available")
except ImportError as e:
    print(f"❌ MCP packages missing: {e}")
    print("   Install with: pip install mcp fastmcp")
    exit(1)
print()

# Test 4: Try to create server instance
print("-" * 80)
print("TEST 4: Create server instance")
print("-" * 80)
try:
    test_server = server_module.create_stock_server()
    print(f"✅ Server instance created: {test_server}")
except Exception as e:
    print(f"❌ Failed to create server: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
print()

# Test 5: Try to start server as subprocess (with timeout)
print("-" * 80)
print("TEST 5: Start server as subprocess")
print("-" * 80)
print("Starting server process (will timeout after 5 seconds)...")

try:
    proc = subprocess.Popen(
        ["python", server_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit to see if it crashes immediately
    time.sleep(2)
    
    # Check if still running
    if proc.poll() is None:
        print("✅ Server process started and is running")
        print(f"   PID: {proc.pid}")
        
        # Kill it
        proc.terminate()
        time.sleep(1)
        if proc.poll() is None:
            proc.kill()
        print("   Server terminated successfully")
    else:
        # Process ended
        stdout, stderr = proc.communicate()
        print(f"❌ Server process ended immediately")
        print(f"   Exit code: {proc.returncode}")
        if stdout:
            print(f"   STDOUT: {stdout}")
        if stderr:
            print(f"   STDERR: {stderr}")
        exit(1)
        
except Exception as e:
    print(f"❌ Failed to start server: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
print()

# Summary
print("=" * 80)
print("🎉 ALL TESTS PASSED!")
print("=" * 80)
print()
print("The MCP server can:")
print("  ✅ Be imported")
print("  ✅ Create instances")
print("  ✅ Start as a subprocess")
print()
print("Next step: Test MCP client connection with:")
print("  python test_mcp_simple.py")
print()

