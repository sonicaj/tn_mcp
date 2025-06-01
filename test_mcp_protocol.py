#!/usr/bin/env python3
"""Test MCP protocol communication directly"""

import asyncio
import json
import sys


async def test_mcp_communication():
    """Test basic MCP communication"""
    # Send initialization request
    request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    print(json.dumps(request), flush=True)
    sys.stdout.flush()
    
    # Wait a bit for response
    await asyncio.sleep(0.5)
    
    # Try to list tools
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    print(json.dumps(request), flush=True)
    sys.stdout.flush()
    
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(test_mcp_communication())