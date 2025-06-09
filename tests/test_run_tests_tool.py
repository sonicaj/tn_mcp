#!/usr/bin/env python3
"""
Test the truenas_run_tests tool functionality
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from truenas_mcp_tools_server import TrueNASDocToolsServer
from mcp.types import Tool, TextContent


class TestRunTestsTool:
    """Test the truenas_run_tests tool."""
    
    @pytest.fixture
    def server(self, tmp_path):
        """Create a server instance for testing."""
        # Create a minimal docs structure
        docs_path = tmp_path / "docs"
        docs_path.mkdir()
        (docs_path / "CLAUDE.md").write_text("# Test Overview")
        
        return TrueNASDocToolsServer(str(docs_path))
    
    @pytest.mark.asyncio
    async def test_tool_is_registered(self, server):
        """Test that the run_tests tool is properly registered."""
        tools = await server.handle_list_tools()
        tool_names = [tool.name for tool in tools]
        
        assert "truenas_run_tests" in tool_names
        
        # Find the tool and check its properties
        run_tests_tool = next(tool for tool in tools if tool.name == "truenas_run_tests")
        assert run_tests_tool.description == "Run TrueNAS middleware tests using Docker. Can run all tests or specific test files."
        
        # Check input schema
        schema = run_tests_tool.inputSchema
        assert schema["type"] == "object"
        assert "repo_path" in schema["properties"]
        assert "test_file" in schema["properties"]
        assert schema["required"] == []
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_run_all_tests_success(self, mock_subprocess, server):
        """Test running all tests successfully."""
        # Mock successful test output
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            b"Running middleware unit tests from: /path/to/middleware\n"
            b"============================= test session starts ==============================\n"
            b"platform linux -- Python 3.11.9, pytest-7.2.1\n"
            b"collected 100 items\n"
            b"\n"
            b"test_example.py::test_one PASSED [ 1%]\n"
            b"test_example.py::test_two PASSED [ 2%]\n"
            b"====================== 100 passed, 0 warnings in 120.00s ======================\n"
            b"Tests completed!",
            b""
        ))
        mock_subprocess.return_value = mock_process
        
        # Call the tool
        result = await server.handle_call_tool("truenas_run_tests", {})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "✅ Tests completed successfully!" in result[0].text
        assert "test session starts" in result[0].text
        assert "100 passed" in result[0].text
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_run_specific_test_file(self, mock_subprocess, server):
        """Test running a specific test file."""
        # Mock successful test output for specific file
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            b"Searching for test file: test_construct_schema.py\n"
            b"Found test file at: /usr/local/lib/python3.11/dist-packages/middlewared/pytest/unit/plugins/apps/test_construct_schema.py\n"
            b"============================= test session starts ==============================\n"
            b"platform linux -- Python 3.11.9, pytest-7.2.1\n"
            b"collected 4 items\n"
            b"\n"
            b"test_construct_schema.py::test_construct_schema_update_False PASSED [ 25%]\n"
            b"test_construct_schema.py::test_construct_schema_update_True PASSED [ 50%]\n"
            b"test_construct_schema.py::test_construct_schema_KeyError PASSED [ 75%]\n"
            b"test_construct_schema.py::test_construct_schema_ValidationError PASSED [100%]\n"
            b"====================== 4 passed, 0 warnings in 31.68s ======================\n",
            b""
        ))
        mock_subprocess.return_value = mock_process
        
        # Call the tool with test file
        result = await server.handle_call_tool("truenas_run_tests", {
            "test_file": "test_construct_schema.py"
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "✅ Tests completed successfully!" in result[0].text
        assert "test_construct_schema.py" in result[0].text
        assert "4 passed" in result[0].text
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_run_tests_failure(self, mock_subprocess, server):
        """Test handling test failures."""
        # Mock failed test output
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(
            b"Running tests...\n"
            b"============================= test session starts ==============================\n"
            b"collected 5 items\n"
            b"\n"
            b"test_example.py::test_one PASSED [ 20%]\n"
            b"test_example.py::test_two FAILED [ 40%]\n"
            b"====================== 1 failed, 1 passed in 10.00s ======================\n",
            b"Error: Test failed\n"
        ))
        mock_subprocess.return_value = mock_process
        
        # Call the tool
        result = await server.handle_call_tool("truenas_run_tests", {})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "❌ Tests failed with exit code: 1" in result[0].text
        assert "1 failed, 1 passed" in result[0].text
        assert "Error: Test failed" in result[0].text
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_run_tests_timeout(self, mock_subprocess, server):
        """Test handling test timeout."""
        # Mock process that times out
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_subprocess.return_value = mock_process
        
        # Call the tool
        result = await server.handle_call_tool("truenas_run_tests", {})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "❌ Test execution timed out after 10 minutes" in result[0].text
    
    @pytest.mark.asyncio
    async def test_run_tests_script_not_found(self, server):
        """Test handling when test script is not found."""
        # Temporarily rename the script
        script_path = Path(__file__).parent.parent / "run_middleware_tests.sh"
        backup_path = script_path.with_suffix('.sh.bak')
        
        try:
            if script_path.exists():
                script_path.rename(backup_path)
            
            # Call the tool
            result = await server.handle_call_tool("truenas_run_tests", {})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Test script not found" in result[0].text
        finally:
            # Restore the script
            if backup_path.exists():
                backup_path.rename(script_path)
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_run_tests_with_custom_repo_path(self, mock_subprocess, server):
        """Test running tests with custom repository path."""
        # Mock successful test output
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            b"Running middleware unit tests from: /custom/path/middleware\n"
            b"Tests completed successfully!",
            b""
        ))
        mock_subprocess.return_value = mock_process
        
        # Call the tool with custom repo path
        result = await server.handle_call_tool("truenas_run_tests", {
            "repo_path": "/custom/path/middleware"
        })
        
        # Verify the command was called with custom path
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0]
        assert "/custom/path/middleware" in args
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "✅ Tests completed successfully!" in result[0].text
    
    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_output_formatting_no_pytest_output(self, mock_subprocess, server):
        """Test output formatting when pytest output is not found."""
        # Mock output without pytest format
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            b"Line 1\n" * 100 + b"Last line\n",  # 101 lines total
            b""
        ))
        mock_subprocess.return_value = mock_process
        
        # Call the tool
        result = await server.handle_call_tool("truenas_run_tests", {})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "✅ Tests completed successfully!" in result[0].text
        assert "Output (last 50 lines)" in result[0].text
        assert "Last line" in result[0].text


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])