#!/usr/bin/env python3
"""Test script for TrueNAS MCP Server"""

import asyncio
from pathlib import Path
from truenas_mcp_server import TrueNASDocServer


async def test_server():
    """Test the MCP server functionality."""
    # Create server instance with default docs directory
    print("Creating TrueNAS Doc Server...")
    server = TrueNASDocServer()
    
    # Test list resources
    print("\nListing available resources:")
    resources = await server.handle_list_resources()
    for resource in resources[:5]:  # Show first 5
        print(f"  - {resource.name} ({resource.uri})")
    print(f"  ... and {len(resources) - 5} more resources")
    
    # Test read index
    print("\nReading index resource:")
    index_content = await server.handle_read_resource("truenas://index")
    print(index_content[:500] + "..." if len(index_content) > 500 else index_content)
    
    # Test read a specific resource
    if "truenas://overview" in server.resources_cache:
        print("\nReading overview resource:")
        overview = await server.handle_read_resource("truenas://overview")
        print(overview[:500] + "..." if len(overview) > 500 else overview)
    
    print("\nServer test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_server())