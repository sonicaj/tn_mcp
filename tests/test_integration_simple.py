#!/usr/bin/env python3
"""
Simple integration test for the truenas_run_tests tool that can run in Docker.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from truenas_mcp_tools_server import TrueNASDocToolsServer


def test_server_initialization():
    """Test that the server can be initialized."""
    docs_path = Path(__file__).parent.parent / "docs"
    server = TrueNASDocToolsServer(str(docs_path))
    assert server is not None
    assert server.docs_path == docs_path


async def test_tools_list():
    """Test that tools are properly listed."""
    docs_path = Path(__file__).parent.parent / "docs"
    server = TrueNASDocToolsServer(str(docs_path))
    
    tools = await server.handle_list_tools()
    tool_names = [tool.name for tool in tools]
    
    assert "truenas_overview" in tool_names
    assert "truenas_plugin_docs" in tool_names
    assert "truenas_api_docs" in tool_names
    assert "truenas_testing_docs" in tool_names
    assert "truenas_subsystem_docs" in tool_names
    assert "truenas_search_docs" in tool_names
    assert "truenas_run_tests" in tool_names
    
    print(f"✓ Found {len(tools)} tools")
    return True


async def test_overview_tool():
    """Test the overview documentation tool."""
    docs_path = Path(__file__).parent.parent / "docs"
    server = TrueNASDocToolsServer(str(docs_path))
    
    result = await server.handle_call_tool("truenas_overview", {})
    
    assert len(result) == 1
    assert result[0].text is not None
    assert len(result[0].text) > 0
    
    print(f"✓ Overview tool returned {len(result[0].text)} characters")
    return True


def test_sync_tools_list():
    """Synchronous test for pytest."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(test_tools_list())
    assert result is True


def test_sync_overview():
    """Synchronous test for pytest."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(test_overview_tool())
    assert result is True


if __name__ == "__main__":
    # Run tests manually
    print("Running simple integration tests...")
    
    test_server_initialization()
    print("✓ Server initialization test passed")
    
    asyncio.run(test_tools_list())
    asyncio.run(test_overview_tool())
    
    print("\n✅ All integration tests passed!")