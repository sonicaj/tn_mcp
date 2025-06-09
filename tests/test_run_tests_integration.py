#!/usr/bin/env python3
"""
Integration test for the truenas_run_tests tool.
This test actually runs the tool with test_construct_schema.py
"""

import asyncio
import os
from pathlib import Path

# Add the parent directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from truenas_mcp_tools_server import TrueNASDocToolsServer
from mcp.types import TextContent


async def test_run_specific_test():
    """Test running test_construct_schema.py through the MCP tool."""
    # Create server instance
    docs_path = Path(__file__).parent / "docs"
    server = TrueNASDocToolsServer(str(docs_path))
    
    print("Testing truenas_run_tests tool with test_construct_schema.py...")
    
    # Check if the tool is registered
    tools = await server.handle_list_tools()
    tool_names = [tool.name for tool in tools]
    assert "truenas_run_tests" in tool_names, "truenas_run_tests tool not found"
    print("✓ Tool is registered")
    
    # Call the tool with test_construct_schema.py
    print("\nRunning test_construct_schema.py...")
    result = await server.handle_call_tool("truenas_run_tests", {
        "test_file": "test_construct_schema.py"
    })
    
    # Check result
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    
    print("\nResult:")
    print("-" * 80)
    print(result[0].text)
    print("-" * 80)
    
    # Verify key elements in output
    text = result[0].text
    if "✅ Tests completed successfully!" in text:
        print("\n✓ Tests completed successfully")
    else:
        print("\n✗ Tests did not complete successfully")
    
    if "test_construct_schema.py" in text:
        print("✓ Found test_construct_schema.py in output")
    
    if "passed" in text:
        print("✓ Found test results in output")
    
    return "✅" in text  # Return True if tests passed


async def test_tool_without_container():
    """Test the tool when container doesn't exist."""
    # Create server instance
    docs_path = Path(__file__).parent / "docs"
    server = TrueNASDocToolsServer(str(docs_path))
    
    print("\nTesting error handling when container setup is needed...")
    
    # Call the tool (this might fail if container isn't ready)
    result = await server.handle_call_tool("truenas_run_tests", {
        "test_file": "test_construct_schema.py"
    })
    
    print("\nResult:")
    print("-" * 80)
    print(result[0].text)
    print("-" * 80)


async def main():
    """Run all integration tests."""
    print("Running integration tests for truenas_run_tests tool")
    print("=" * 80)
    
    # Test 1: Run specific test file
    try:
        success = await test_run_specific_test()
        if success:
            print("\n✅ Integration test passed!")
        else:
            print("\n❌ Integration test failed!")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Error handling  
    # await test_tool_without_container()


if __name__ == "__main__":
    asyncio.run(main())