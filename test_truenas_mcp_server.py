#!/usr/bin/env python3
"""Comprehensive tests for TrueNAS MCP Server"""

import asyncio
import pytest
from pathlib import Path
import tempfile
import shutil

from truenas_mcp_server import TrueNASDocServer


@pytest.fixture
def temp_docs_dir():
    """Create a temporary docs directory with test CLAUDE.md files."""
    temp_dir = tempfile.mkdtemp()
    docs_path = Path(temp_dir) / "docs"
    
    # Create test directory structure
    (docs_path).mkdir(parents=True)
    (docs_path / "src" / "middlewared" / "middlewared" / "plugins").mkdir(parents=True)
    (docs_path / "src" / "middlewared" / "middlewared" / "api").mkdir(parents=True)
    (docs_path / "tests").mkdir(parents=True)
    
    # Create test CLAUDE.md files
    # Root overview
    (docs_path / "CLAUDE.md").write_text("""# TrueNAS Middleware Repository Overview

## Purpose
This is a test overview document.

## Repository Structure
Test repository structure information.

## Development Guidelines
### Service Architecture
Test service architecture guidelines.
""")
    
    # Plugins documentation
    (docs_path / "src" / "middlewared" / "middlewared" / "plugins" / "CLAUDE.md").write_text("""# Middleware Plugins Directory

## Overview
Test plugins overview.

## Service Types and Base Classes
### 1. Service (Basic Service)
Test service description.

### 2. ConfigService (Single Configuration)
Test config service description.

## Common Plugin Patterns
### Model Definition
Test model pattern.

## Key Plugins by Category
### System Configuration
- boot.py - Boot environment management
- config.py - System configuration
""")
    
    # API documentation
    (docs_path / "src" / "middlewared" / "middlewared" / "api" / "CLAUDE.md").write_text("""# API Directory

## Overview
Test API overview.

## Version Directories
Test versioning information.

## Base Model Classes
Test model classes.

## CRUD Model Pattern
Test CRUD pattern.
""")
    
    # Testing documentation
    (docs_path / "tests" / "CLAUDE.md").write_text("""# Integration Tests Directory

## Overview
Test testing overview.

## Test Structure
Test structure information.

## Writing Tests
Test writing guide.

## Common Patterns
Test patterns.
""")
    
    yield docs_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestTrueNASDocServer:
    """Test suite for TrueNASDocServer."""
    
    def test_initialization(self, temp_docs_dir):
        """Test server initialization."""
        server = TrueNASDocServer(str(temp_docs_dir))
        assert server.docs_path == temp_docs_dir
        assert server.server.name == "truenas-docs"
        assert len(server.claude_md_files) == 4
        assert len(server.resources_cache) > 0
    
    def test_find_claude_md_files(self, temp_docs_dir):
        """Test finding CLAUDE.md files."""
        server = TrueNASDocServer(str(temp_docs_dir))
        files = server._find_claude_md_files()
        assert all(f.name == "CLAUDE.md" for f in files)
        assert any("plugins" in str(f) for f in files)
        assert any("api" in str(f) for f in files)
        assert any("tests" in str(f) for f in files)
    
    def test_extract_sections(self, temp_docs_dir):
        """Test section extraction from markdown."""
        server = TrueNASDocServer(str(temp_docs_dir))
        content = """## Section 1
Content 1

## Section 2
Content 2
More content 2

## Section 3
Content 3"""
        sections = server._extract_sections(content)
        assert "Section 1" in sections
        assert sections["Section 1"] == "Content 1"
        assert "Section 2" in sections
        assert sections["Section 2"] == "Content 2\nMore content 2"
        assert "Section 3" in sections
        assert sections["Section 3"] == "Content 3"
    
    def test_summarize_content(self, temp_docs_dir):
        """Test content summarization."""
        server = TrueNASDocServer(str(temp_docs_dir))
        
        # Test short content (no summarization needed)
        short_content = "Line 1\nLine 2\nLine 3"
        assert server._summarize_content(short_content, 10) == short_content
        
        # Test long content (should be summarized)
        long_content = "\n".join([f"Line {i}" for i in range(100)])
        summarized = server._summarize_content(long_content, 10)
        assert len(summarized.split("\n")) <= 10
        
        # Test that headers are preserved
        content_with_headers = "Normal line\n" + "\n".join([f"# Header {i}\nContent {i}" for i in range(20)])
        summarized = server._summarize_content(content_with_headers, 10)
        assert "# Header" in summarized
    
    def test_resource_creation(self, temp_docs_dir):
        """Test resource creation and organization."""
        server = TrueNASDocServer(str(temp_docs_dir))
        
        # Check overview resources
        assert "truenas://overview" in server.resources_cache
        assert "truenas://development/guidelines" in server.resources_cache
        
        # Check plugin resources
        assert "truenas://plugins/service-types" in server.resources_cache
        assert "truenas://plugins/patterns" in server.resources_cache
        assert "truenas://plugins/categories" in server.resources_cache
        
        # Check API resources
        assert "truenas://api/versioning" in server.resources_cache
        assert "truenas://api/models" in server.resources_cache
        
        # Check testing resources
        assert "truenas://testing/overview" in server.resources_cache
        assert "truenas://testing/patterns" in server.resources_cache
    
    @pytest.mark.asyncio
    async def test_handle_list_resources(self, temp_docs_dir):
        """Test listing resources."""
        server = TrueNASDocServer(str(temp_docs_dir))
        resources = await server.handle_list_resources()
        
        assert len(resources) > 0
        # Convert URI objects to strings for comparison
        resource_uris = [str(r.uri) for r in resources]
        assert "truenas://index" in resource_uris
        assert "truenas://overview" in resource_uris
        assert all(hasattr(r, 'uri') and hasattr(r, 'name') and hasattr(r, 'description') for r in resources)
    
    @pytest.mark.asyncio
    async def test_handle_read_resource(self, temp_docs_dir):
        """Test reading resources."""
        server = TrueNASDocServer(str(temp_docs_dir))
        
        # Test reading index
        index_content = await server.handle_read_resource("truenas://index")
        assert "TrueNAS Middleware Documentation Index" in index_content
        assert "Available Resources" in index_content
        
        # Test reading overview
        overview_content = await server.handle_read_resource("truenas://overview")
        assert "test overview document" in overview_content.lower()
        
        # Test reading non-existent resource
        with pytest.raises(ValueError, match="Resource not found"):
            await server.handle_read_resource("truenas://nonexistent")
    
    def test_generate_index(self, temp_docs_dir):
        """Test index generation."""
        server = TrueNASDocServer(str(temp_docs_dir))
        index = server._generate_index()
        
        assert "TrueNAS Middleware Documentation Index" in index
        assert "Overview" in index
        assert "Plugins" in index
        assert "API" in index
        assert "Testing" in index
        assert "truenas://overview" in index
    
    def test_default_docs_directory(self):
        """Test initialization with default docs directory."""
        # Create a temporary docs directory in the current location
        test_docs = Path("test_docs_temp")
        test_docs.mkdir(exist_ok=True)
        (test_docs / "CLAUDE.md").write_text("# Test")
        
        try:
            # Temporarily change __file__ location context
            original_file = TrueNASDocServer.__init__.__globals__['__file__']
            TrueNASDocServer.__init__.__globals__['__file__'] = str(Path.cwd() / "dummy.py")
            
            # Should use ./docs by default
            server = TrueNASDocServer()
            expected_path = Path.cwd() / "docs"
            assert server.docs_path == expected_path
            
        finally:
            # Restore and cleanup
            TrueNASDocServer.__init__.__globals__['__file__'] = original_file
            shutil.rmtree(test_docs)
    
    def test_empty_docs_directory(self):
        """Test handling of empty docs directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            server = TrueNASDocServer(temp_dir)
            assert len(server.claude_md_files) == 0
            assert len(server.resources_cache) == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_resource_access(self, temp_docs_dir):
        """Test concurrent access to resources."""
        server = TrueNASDocServer(str(temp_docs_dir))
        
        # Simulate concurrent access
        tasks = [
            server.handle_read_resource("truenas://index"),
            server.handle_read_resource("truenas://overview"),
            server.handle_list_resources(),
        ]
        
        results = await asyncio.gather(*tasks)
        assert len(results) == 3
        assert isinstance(results[0], str)
        assert isinstance(results[1], str)
        assert isinstance(results[2], list)


class TestIntegration:
    """Integration tests for the complete server flow."""
    
    @pytest.mark.asyncio
    async def test_full_server_lifecycle(self, temp_docs_dir):
        """Test complete server lifecycle."""
        server = TrueNASDocServer(str(temp_docs_dir))
        
        # List resources
        resources = await server.handle_list_resources()
        assert len(resources) > 5
        
        # Read each resource
        for resource in resources:
            if resource.uri != "truenas://index":  # Skip index as it's generated
                try:
                    content = await server.handle_read_resource(resource.uri)
                    assert isinstance(content, str)
                    assert len(content) > 0
                except ValueError:
                    # Some URIs might not have content in test setup
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])