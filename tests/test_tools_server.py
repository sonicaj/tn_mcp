#!/usr/bin/env python3
"""
Test script for TrueNAS MCP Tools Server
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_tools_server():
    """Test the TrueNAS MCP tools server."""
    server_params = StdioServerParameters(
        command="python",
        args=["truenas_mcp_tools_server.py"],
        env={"MCP_SERVER_MODE": "debug"}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            print("\n=== Available Tools ===")
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"\nTool: {tool.name}")
                print(f"  Description: {tool.description}")
                print(f"  Schema: {json.dumps(tool.inputSchema, indent=2)}")

            # Test 1: Get overview
            print("\n\n=== Test 1: Overview ===")
            result = await session.call_tool("truenas_overview", {})
            print(result.content[0].text[:500] + "...")

            # Test 2: Get plugin documentation (general)
            print("\n\n=== Test 2: Plugin Documentation (Service Types) ===")
            result = await session.call_tool("truenas_plugin_docs", {
                "topic": "service_types"
            })
            print(result.content[0].text[:500] + "...")

            # Test 3: Get specific plugin documentation
            print("\n\n=== Test 3: Specific Plugin (SMB) ===")
            result = await session.call_tool("truenas_plugin_docs", {
                "plugin_name": "smb"
            })
            print(result.content[0].text[:500] + "...")

            # Test 4: Get API documentation
            print("\n\n=== Test 4: API Documentation (Versioning) ===")
            result = await session.call_tool("truenas_api_docs", {
                "topic": "versioning"
            })
            print(result.content[0].text[:500] + "...")

            # Test 5: Search documentation
            print("\n\n=== Test 5: Search for 'CRUD' ===")
            result = await session.call_tool("truenas_search_docs", {
                "query": "CRUD"
            })
            print(result.content[0].text[:500] + "...")

            print("\n\nAll tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_tools_server())