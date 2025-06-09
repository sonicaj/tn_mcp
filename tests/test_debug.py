#!/usr/bin/env python3
"""Test script to debug resource creation"""

import asyncio
from pathlib import Path
from truenas_mcp_server import TrueNASDocServer

async def test_server():
    # Create server instance
    server = TrueNASDocServer()
    
    print("\n=== CLAUDE.md Files Found ===")
    for file in server.claude_md_files:
        print(f"  - {file}")
    
    print(f"\n=== Total Resources Created: {len(server.resources_cache)} ===")
    for uri, resource in sorted(server.resources_cache.items()):
        print(f"  - {uri}: {resource['name']}")
    
    # Test reading a specific resource
    if "truenas://api/versioning" in server.resources_cache:
        print("\n=== API Versioning Resource Content (first 500 chars) ===")
        content = server.resources_cache["truenas://api/versioning"]["content"]
        print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print("\n!!! API Versioning resource not found !!!")

if __name__ == "__main__":
    asyncio.run(test_server())