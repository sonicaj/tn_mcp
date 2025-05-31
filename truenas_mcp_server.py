#!/usr/bin/env python3
"""
TrueNAS Middleware MCP Server

This MCP server provides documentation resources from the TrueNAS middleware repository
to Code Claude, helping it understand the codebase structure and APIs.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent


class TrueNASDocServer:
    def __init__(self, docs_path: str = None):
        # Default to local docs directory
        if docs_path is None:
            docs_path = Path(__file__).parent / "docs"
        self.docs_path = Path(docs_path)
        self.server = Server("truenas-docs")
        self.claude_md_files = self._find_claude_md_files()
        self.resources_cache: Dict[str, Dict[str, Any]] = {}
        
        # Register handlers
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            return await self.handle_list_resources()
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            return await self.handle_read_resource(uri)
        
        # Pre-process and categorize documentation
        self._process_documentation()
    
    def _find_claude_md_files(self) -> List[Path]:
        """Find all CLAUDE.md files in the docs directory."""
        claude_files = []
        for path in self.docs_path.rglob("CLAUDE.md"):
            claude_files.append(path)
        return sorted(claude_files)
    
    def _process_documentation(self):
        """Process CLAUDE.md files and create optimized resources."""
        # Categories for organizing documentation
        categories = {
            "overview": [],
            "plugins": [],
            "api": [],
            "testing": [],
            "subsystems": {}
        }
        
        for claude_file in self.claude_md_files:
            relative_path = claude_file.relative_to(self.docs_path)
            content = claude_file.read_text()
            
            # Categorize based on path
            if relative_path.name == "CLAUDE.md" and relative_path.parent == Path("."):
                # Root CLAUDE.md - overview
                self._create_overview_resources(content)
            elif "plugins" in str(relative_path):
                # Plugin documentation
                plugin_name = relative_path.parent.name
                if plugin_name == "plugins":
                    # General plugins documentation
                    self._create_plugins_overview(content)
                else:
                    # Specific plugin documentation
                    self._create_plugin_resource(plugin_name, content, relative_path)
            elif "api" in str(relative_path):
                # API documentation
                self._create_api_resources(content)
            elif "tests" in str(relative_path):
                # Testing documentation
                self._create_testing_resources(content)
            else:
                # Other subsystem documentation
                self._create_subsystem_resource(relative_path, content)
    
    def _create_overview_resources(self, content: str):
        """Create overview resources from root CLAUDE.md."""
        # Extract key sections
        sections = self._extract_sections(content)
        
        # Create main overview resource
        self.resources_cache["truenas://overview"] = {
            "name": "TrueNAS Middleware Overview",
            "description": "High-level overview of the TrueNAS middleware architecture",
            "content": self._summarize_content(sections.get("Purpose", "") + "\n\n" + 
                                             sections.get("Repository Structure", ""))
        }
        
        # Create development guidelines resource
        if "Development Guidelines" in sections:
            self.resources_cache["truenas://development/guidelines"] = {
                "name": "Development Guidelines",
                "description": "Best practices for TrueNAS middleware development",
                "content": sections["Development Guidelines"]
            }
    
    def _create_plugins_overview(self, content: str):
        """Create plugins overview resource."""
        sections = self._extract_sections(content)
        
        # Create service types reference
        if "Service Types and Base Classes" in sections:
            self.resources_cache["truenas://plugins/service-types"] = {
                "name": "Service Types Reference",
                "description": "Guide to different service base classes (Service, ConfigService, CRUDService, SystemServiceService)",
                "content": sections["Service Types and Base Classes"]
            }
        
        # Create plugin patterns reference
        if "Common Plugin Patterns" in sections:
            self.resources_cache["truenas://plugins/patterns"] = {
                "name": "Plugin Development Patterns",
                "description": "Common patterns for implementing TrueNAS plugins",
                "content": sections["Common Plugin Patterns"]
            }
        
        # Create plugin categories reference
        if "Key Plugins by Category" in sections:
            self.resources_cache["truenas://plugins/categories"] = {
                "name": "Plugin Categories",
                "description": "Categorized list of all plugins and their purposes",
                "content": sections["Key Plugins by Category"]
            }
    
    def _create_plugin_resource(self, plugin_name: str, content: str, path: Path):
        """Create resource for specific plugin."""
        sections = self._extract_sections(content)
        
        # Create concise plugin documentation
        summary = self._create_plugin_summary(plugin_name, sections)
        
        self.resources_cache[f"truenas://plugins/{plugin_name}"] = {
            "name": f"{plugin_name.title()} Plugin",
            "description": f"Documentation for the {plugin_name} plugin",
            "content": summary
        }
    
    def _create_api_resources(self, content: str):
        """Create API-related resources."""
        sections = self._extract_sections(content)
        
        # API versioning guide
        if "Version Directories" in sections or "Migration Between Versions" in sections:
            self.resources_cache["truenas://api/versioning"] = {
                "name": "API Versioning",
                "description": "How API versioning works in TrueNAS middleware",
                "content": sections.get("Overview", "") + "\n\n" + 
                         sections.get("Version Directories", "") + "\n\n" +
                         sections.get("Migration Between Versions", "")
            }
        
        # Pydantic models guide
        if "Base Model Classes" in sections or "CRUD Model Pattern" in sections:
            self.resources_cache["truenas://api/models"] = {
                "name": "API Model Patterns",
                "description": "How to define Pydantic models for API endpoints",
                "content": sections.get("Base Model Classes", "") + "\n\n" +
                         sections.get("CRUD Model Pattern", "") + "\n\n" +
                         sections.get("Special Types and Fields", "")
            }
    
    def _create_testing_resources(self, content: str):
        """Create testing-related resources."""
        sections = self._extract_sections(content)
        
        # Testing overview
        self.resources_cache["truenas://testing/overview"] = {
            "name": "Testing Guide",
            "description": "How to write and run integration tests for TrueNAS",
            "content": sections.get("Overview", "") + "\n\n" +
                     sections.get("Test Structure", "") + "\n\n" +
                     sections.get("Writing Tests", "")
        }
        
        # Testing patterns
        if "Common Patterns" in sections:
            self.resources_cache["truenas://testing/patterns"] = {
                "name": "Testing Patterns",
                "description": "Common patterns for writing TrueNAS tests",
                "content": sections["Common Patterns"]
            }
    
    def _create_subsystem_resource(self, path: Path, content: str):
        """Create resource for other subsystems."""
        subsystem = path.parent.name
        sections = self._extract_sections(content)
        
        # Create concise subsystem documentation
        summary = self._create_subsystem_summary(subsystem, sections)
        
        self.resources_cache[f"truenas://subsystems/{subsystem}"] = {
            "name": f"{subsystem.title()} Subsystem",
            "description": f"Documentation for the {subsystem} subsystem",
            "content": summary
        }
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from markdown content."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _summarize_content(self, content: str, max_lines: int = 50) -> str:
        """Create a concise summary of content to avoid context overload."""
        lines = content.split('\n')
        if len(lines) <= max_lines:
            return content
        
        # Keep the most important parts
        summary_lines = []
        in_code_block = False
        code_block_count = 0
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if in_code_block:
                    code_block_count += 1
                # Skip code blocks after the first few
                if code_block_count > 2:
                    continue
            
            # Always include headers and important markers
            if (line.startswith('#') or 
                line.startswith('- **') or
                line.strip().startswith('**') or
                (not in_code_block and len(summary_lines) < max_lines)):
                summary_lines.append(line)
        
        return '\n'.join(summary_lines)
    
    def _create_plugin_summary(self, plugin_name: str, sections: Dict[str, str]) -> str:
        """Create a concise summary for a plugin."""
        summary_parts = []
        
        # Always include overview if present
        if "Overview" in sections:
            summary_parts.append(f"## Overview\n{sections['Overview']}")
        
        # Include key concepts/architecture
        for key in ["Architecture", "Core Concepts", "Key Concepts"]:
            if key in sections:
                summary_parts.append(f"## {key}\n{self._summarize_content(sections[key], 30)}")
                break
        
        # Include main operations/methods
        for key in ["Core Components", "Key Methods", "Operations", "Main Operations"]:
            if key in sections:
                summary_parts.append(f"## {key}\n{self._summarize_content(sections[key], 40)}")
                break
        
        return '\n\n'.join(summary_parts)
    
    def _create_subsystem_summary(self, subsystem: str, sections: Dict[str, str]) -> str:
        """Create a concise summary for a subsystem."""
        return self._create_plugin_summary(subsystem, sections)
    
    async def handle_list_resources(self) -> List[Resource]:
        """Handle list_resources request."""
        resources = []
        
        # Add index resource
        resources.append(Resource(
            uri="truenas://index",
            name="TrueNAS Documentation Index",
            description="Index of all available TrueNAS middleware documentation",
            mimeType="text/plain"
        ))
        
        # Add all processed resources
        for uri, resource_data in self.resources_cache.items():
            resources.append(Resource(
                uri=uri,
                name=resource_data["name"],
                description=resource_data["description"],
                mimeType="text/plain"
            ))
        
        return resources
    
    async def handle_read_resource(self, uri: str) -> str:
        """Handle read_resource request."""
        if uri == "truenas://index":
            # Generate index content
            return self._generate_index()
        
        if uri in self.resources_cache:
            return self.resources_cache[uri]["content"]
        
        raise ValueError(f"Resource not found: {uri}")
    
    def _generate_index(self) -> str:
        """Generate an index of all available resources."""
        index_lines = ["# TrueNAS Middleware Documentation Index\n"]
        index_lines.append("This MCP server provides documentation resources for the TrueNAS middleware codebase.\n")
        index_lines.append("## Available Resources\n")
        
        # Group resources by category
        categories = {
            "Overview": [],
            "Development": [],
            "Plugins": [],
            "API": [],
            "Testing": [],
            "Subsystems": []
        }
        
        for uri, resource_data in sorted(self.resources_cache.items()):
            entry = f"- **{resource_data['name']}** (`{uri}`): {resource_data['description']}"
            
            if "overview" in uri:
                categories["Overview"].append(entry)
            elif "development" in uri:
                categories["Development"].append(entry)
            elif "plugins" in uri:
                categories["Plugins"].append(entry)
            elif "api" in uri:
                categories["API"].append(entry)
            elif "testing" in uri:
                categories["Testing"].append(entry)
            elif "subsystems" in uri:
                categories["Subsystems"].append(entry)
        
        # Add categorized entries to index
        for category, entries in categories.items():
            if entries:
                index_lines.append(f"\n### {category}\n")
                index_lines.extend(entries)
        
        return '\n'.join(index_lines)
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


async def main():
    """Main entry point."""
    # Create and run server with default docs directory
    doc_server = TrueNASDocServer()
    await doc_server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())