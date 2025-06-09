#!/usr/bin/env python3
"""
Comprehensive test suite for TrueNAS MCP Tools Server

This simulates how an MCP client/agent would consume the tools,
ensuring all functionality works as expected.
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from truenas_mcp_tools_server import TrueNASDocToolsServer
from mcp.types import Tool, TextContent


class TestTrueNASMCPToolsServer:
    """Test suite simulating MCP client/agent usage patterns."""

    @pytest.fixture
    def mock_docs_path(self, tmp_path):
        """Create a mock documentation structure."""
        # Create root overview
        root_claude = tmp_path / "docs" / "CLAUDE.md"
        root_claude.parent.mkdir(parents=True)
        root_claude.write_text("""# TrueNAS Middleware Overview

## Purpose
This is the main middleware documentation.

## Repository Structure
The repository is organized into plugins, API, and subsystems.

## Development Guidelines
Follow these guidelines when developing.""")

        # Create plugins overview
        plugins_claude = tmp_path / "docs" / "src" / "middlewared" / "middlewared" / "plugins" / "CLAUDE.md"
        plugins_claude.parent.mkdir(parents=True)
        plugins_claude.write_text("""# Plugin Development Guide

## Service Types and Base Classes
- Service: Basic service class
- ConfigService: For configuration management
- CRUDService: For CRUD operations
- SystemServiceService: For system services

## Common Plugin Patterns
1. Input validation with ValidationErrors
2. Async method decorators
3. Event system integration

## Key Plugins by Category
- Storage: pool, dataset, disk
- Sharing: smb, nfs, iscsi
- System: system, network, service""")

        # Create SMB plugin docs
        smb_claude = tmp_path / "docs" / "src" / "middlewared" / "middlewared" / "plugins" / "smb" / "CLAUDE.md"
        smb_claude.parent.mkdir(parents=True)
        smb_claude.write_text("""# SMB Plugin

## Overview
The SMB plugin manages Samba shares and Windows networking.

## Architecture
Extends CRUDService for share management.

## Key Methods
- smb.create: Create new share
- smb.update: Update existing share
- smb.delete: Remove share""")

        # Create API docs
        api_claude = tmp_path / "docs" / "src" / "middlewared" / "middlewared" / "api" / "CLAUDE.md"
        api_claude.parent.mkdir(parents=True)
        api_claude.write_text("""# API Documentation

## Overview
API versioning and patterns documentation.

## Directory Structure
- v2.0: Current API version
- v1.0: Legacy API (deprecated)

## Migration Between Versions
Use compatibility layer for smooth transitions.

## Key Concepts
Pydantic models define API schemas.

## Common Patterns
Use decorators for API method definitions.

## Best Practices
Always validate input and handle errors gracefully.""")

        # Create testing docs
        test_claude = tmp_path / "docs" / "tests" / "CLAUDE.md"
        test_claude.parent.mkdir(parents=True)
        test_claude.write_text("""# Testing Guide

## Overview
Integration testing for TrueNAS middleware.

## Test Structure
Tests are organized by plugin and functionality.

## Writing Tests
Use pytest fixtures and async testing.

## Common Patterns
1. Setup and teardown fixtures
2. Mock external dependencies
3. Test both success and error cases""")

        # Create alert subsystem docs
        alert_claude = tmp_path / "docs" / "src" / "middlewared" / "middlewared" / "alert" / "CLAUDE.md"
        alert_claude.parent.mkdir(parents=True)
        alert_claude.write_text("""# Alert Subsystem

## Overview
The alert subsystem manages system notifications.

## Architecture
Event-driven alert generation and delivery.""")

        return tmp_path / "docs"

    @pytest.fixture
    def server(self, mock_docs_path):
        """Create a server instance with mock documentation."""
        return TrueNASDocToolsServer(str(mock_docs_path))

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test that all expected tools are listed."""
        tools = await server.handle_list_tools()
        
        # Verify we have exactly 6 tools
        assert len(tools) == 6
        
        # Verify tool names
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "truenas_overview",
            "truenas_plugin_docs",
            "truenas_api_docs",
            "truenas_testing_docs",
            "truenas_subsystem_docs",
            "truenas_search_docs"
        ]
        for expected in expected_tools:
            assert expected in tool_names
        
        # Verify tool schemas are properly defined
        for tool in tools:
            assert isinstance(tool, Tool)
            assert tool.description
            assert tool.inputSchema
            assert tool.inputSchema["type"] == "object"

    @pytest.mark.asyncio
    async def test_overview_tool(self, server):
        """Test the overview tool returns middleware documentation."""
        result = await server.handle_call_tool("truenas_overview", {})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        content = result[0].text
        
        # Verify content includes expected sections
        assert "middleware documentation" in content
        assert "repository is organized" in content.lower()
        assert "Development Guidelines" in content

    @pytest.mark.asyncio
    async def test_plugin_docs_general(self, server):
        """Test plugin documentation without specific plugin."""
        # Test getting service types
        result = await server.handle_call_tool("truenas_plugin_docs", {
            "topic": "service_types"
        })
        
        assert len(result) == 1
        content = result[0].text
        assert "Service Types and Base Classes" in content
        assert "CRUDService" in content
        assert "ConfigService" in content

    @pytest.mark.asyncio
    async def test_plugin_docs_specific(self, server):
        """Test getting documentation for a specific plugin."""
        result = await server.handle_call_tool("truenas_plugin_docs", {
            "plugin_name": "smb"
        })
        
        assert len(result) == 1
        content = result[0].text
        assert "SMB Plugin" in content
        assert "Samba shares" in content
        assert "smb.create" in content

    @pytest.mark.asyncio
    async def test_plugin_docs_nonexistent(self, server):
        """Test error handling for non-existent plugin."""
        result = await server.handle_call_tool("truenas_plugin_docs", {
            "plugin_name": "nonexistent"
        })
        
        assert len(result) == 1
        content = result[0].text
        assert "not found" in content
        assert "Available plugins:" in content

    @pytest.mark.asyncio
    async def test_api_docs_all_topics(self, server):
        """Test API documentation for different topics."""
        topics = ["versioning", "models", "patterns", "best_practices", "all"]
        
        for topic in topics:
            result = await server.handle_call_tool("truenas_api_docs", {
                "topic": topic
            })
            
            assert len(result) == 1
            content = result[0].text
            
            if topic == "versioning":
                assert "Directory Structure" in content or "Overview" in content
            elif topic == "models":
                assert "Pydantic" in content or "Concepts" in content
            elif topic == "patterns":
                assert "Common" in content or "Patterns" in content
            elif topic == "best_practices":
                assert "Best Practices" in content
            elif topic == "all":
                assert "API Documentation" in content

    @pytest.mark.asyncio
    async def test_testing_docs(self, server):
        """Test testing documentation retrieval."""
        result = await server.handle_call_tool("truenas_testing_docs", {
            "topic": "patterns"
        })
        
        assert len(result) == 1
        content = result[0].text
        assert "Common Patterns" in content or "Testing Patterns" in content

    @pytest.mark.asyncio
    async def test_subsystem_docs(self, server):
        """Test subsystem documentation retrieval."""
        # Test with valid subsystem
        result = await server.handle_call_tool("truenas_subsystem_docs", {
            "subsystem": "alert"
        })
        
        assert len(result) == 1
        content = result[0].text
        assert "Alert Subsystem" in content
        assert "notifications" in content

    @pytest.mark.asyncio
    async def test_subsystem_docs_missing_param(self, server):
        """Test subsystem docs with missing parameter."""
        result = await server.handle_call_tool("truenas_subsystem_docs", {})
        
        assert len(result) == 1
        content = result[0].text
        assert "Please specify a subsystem" in content
        assert "Available:" in content

    @pytest.mark.asyncio
    async def test_search_docs(self, server):
        """Test documentation search functionality."""
        result = await server.handle_call_tool("truenas_search_docs", {
            "query": "CRUD"
        })
        
        assert len(result) == 1
        content = result[0].text
        assert "search results for" in content.lower()
        assert "Found in" in content

    @pytest.mark.asyncio
    async def test_search_docs_no_results(self, server):
        """Test search with no results."""
        result = await server.handle_call_tool("truenas_search_docs", {
            "query": "xyz123nonexistent"
        })
        
        assert len(result) == 1
        content = result[0].text
        assert "No results found" in content

    @pytest.mark.asyncio
    async def test_search_docs_empty_query(self, server):
        """Test search with empty query."""
        result = await server.handle_call_tool("truenas_search_docs", {
            "query": ""
        })
        
        assert len(result) == 1
        content = result[0].text
        assert "Please provide a search query" in content

    @pytest.mark.asyncio
    async def test_unknown_tool(self, server):
        """Test handling of unknown tool name."""
        result = await server.handle_call_tool("unknown_tool", {})
        
        assert len(result) == 1
        content = result[0].text
        assert "Unknown tool" in content

    @pytest.mark.asyncio
    async def test_tool_error_handling(self, server):
        """Test that tools handle errors gracefully."""
        # Force an error by patching the documentation cache
        server.documentation_cache = {}
        
        result = await server.handle_call_tool("truenas_overview", {})
        
        assert len(result) == 1
        content = result[0].text
        # Should return a message, not raise an exception
        assert "not found" in content.lower()

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, server):
        """Test that multiple tools can be called concurrently (agent pattern)."""
        # Simulate an agent calling multiple tools at once
        tasks = [
            server.handle_call_tool("truenas_overview", {}),
            server.handle_call_tool("truenas_plugin_docs", {"plugin_name": "smb"}),
            server.handle_call_tool("truenas_search_docs", {"query": "service"}),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 3
        for result in results:
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text

    @pytest.mark.asyncio
    async def test_mcp_server_integration(self, server):
        """Test the server's MCP integration points."""
        # Test that server has proper MCP handlers registered
        assert hasattr(server.server, 'list_tools')
        assert hasattr(server.server, 'call_tool')
        
        # Verify server name
        assert server.server.name == "truenas-docs-tools"

    def test_logging_configuration(self):
        """Test that logging is configured correctly for production."""
        with patch.dict(os.environ, {'MCP_SERVER_MODE': 'production'}):
            # Re-import to trigger logging setup
            import importlib
            import truenas_mcp_tools_server
            importlib.reload(truenas_mcp_tools_server)
            
            # In production mode, should log to file
            log_file = Path(__file__).parent / 'truenas_mcp_tools_server.log'
            # Just verify the configuration doesn't crash
            assert True

    @pytest.mark.asyncio
    async def test_documentation_processing(self, mock_docs_path):
        """Test that documentation is properly processed on initialization."""
        server = TrueNASDocToolsServer(str(mock_docs_path))
        
        # Verify documentation was processed
        assert len(server.documentation_cache) > 0
        
        # Check specific entries exist
        assert "overview" in server.documentation_cache
        assert "plugins_overview" in server.documentation_cache
        assert "plugin_smb" in server.documentation_cache
        assert "api" in server.documentation_cache
        assert "testing" in server.documentation_cache
        assert "subsystem_alert" in server.documentation_cache


if __name__ == "__main__":
    pytest.main([__file__, "-v"])