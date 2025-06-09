#!/usr/bin/env python3
"""
TrueNAS Middleware MCP Tools Server

This MCP server provides documentation tools (instead of resources) from the TrueNAS 
middleware repository to Code Claude, helping it understand the codebase structure and APIs.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os
import subprocess
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Set up logging - use file logging when running as MCP server to avoid stdio conflicts
if os.environ.get('MCP_SERVER_MODE') == 'production':
    # Log to file in production MCP mode
    log_file = Path(__file__).parent / 'truenas_mcp_tools_server.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=str(log_file),
        filemode='a'
    )
else:
    # Console logging for testing/debugging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)


class TrueNASDocToolsServer:
    def __init__(self, docs_path: str = None):
        # Default to local docs directory
        if docs_path is None:
            docs_path = Path(__file__).parent / "docs"
        self.docs_path = Path(docs_path)
        logger.info(f"Initializing TrueNAS Doc Tools Server with docs path: {self.docs_path}")
        
        self.server = Server("truenas-docs-tools")
        self.claude_md_files = self._find_claude_md_files()
        self.documentation_cache: Dict[str, Dict[str, Any]] = {}

        # Register tool handlers
        @self.server.list_tools()
        async def list_tools_handler() -> List[Tool]:
            return await self.handle_list_tools()

        @self.server.call_tool()
        async def call_tool_handler(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            return await self.handle_call_tool(name, arguments)

        # Pre-process and categorize documentation
        self._process_documentation()
        logger.info(f"Server initialized with documentation processed")

    def _find_claude_md_files(self) -> List[Path]:
        """Find all CLAUDE.md files in the docs directory."""
        claude_files = []
        for path in self.docs_path.rglob("CLAUDE.md"):
            claude_files.append(path)
        logger.debug(f"Found {len(claude_files)} CLAUDE.md files")
        return sorted(claude_files)

    def _process_documentation(self):
        """Process CLAUDE.md files and create documentation cache."""
        logger.debug("Processing documentation files...")

        for claude_file in self.claude_md_files:
            relative_path = claude_file.relative_to(self.docs_path)
            content = claude_file.read_text()

            # Categorize based on path
            if relative_path.name == "CLAUDE.md" and relative_path.parent == Path("."):
                # Root CLAUDE.md - overview
                self._cache_overview_content(content)
            elif "plugins" in str(relative_path):
                # Plugin documentation
                plugin_name = relative_path.parent.name
                if plugin_name == "plugins":
                    # General plugins documentation
                    self._cache_plugins_overview(content)
                else:
                    # Specific plugin documentation
                    self._cache_plugin_content(plugin_name, content, relative_path)
            elif "api" in str(relative_path):
                # API documentation
                self._cache_api_content(content)
            elif "tests" in str(relative_path):
                # Testing documentation
                self._cache_testing_content(content)
            else:
                # Other subsystem documentation
                self._cache_subsystem_content(relative_path, content)
        
        logger.debug(f"Documentation processing complete")

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

    def _cache_overview_content(self, content: str):
        """Cache overview content."""
        sections = self._extract_sections(content)
        self.documentation_cache["overview"] = {
            "content": self._summarize_content(
                sections.get("Purpose", "") + "\n\n" +
                sections.get("Repository Structure", "")
            ),
            "sections": sections
        }

    def _cache_plugins_overview(self, content: str):
        """Cache plugins overview content."""
        sections = self._extract_sections(content)
        self.documentation_cache["plugins_overview"] = {
            "content": content,
            "sections": sections
        }

    def _cache_plugin_content(self, plugin_name: str, content: str, path: Path):
        """Cache specific plugin content."""
        sections = self._extract_sections(content)
        self.documentation_cache[f"plugin_{plugin_name}"] = {
            "content": content,
            "sections": sections
        }

    def _cache_api_content(self, content: str):
        """Cache API content."""
        sections = self._extract_sections(content)
        self.documentation_cache["api"] = {
            "content": content,
            "sections": sections
        }

    def _cache_testing_content(self, content: str):
        """Cache testing content."""
        sections = self._extract_sections(content)
        self.documentation_cache["testing"] = {
            "content": content,
            "sections": sections
        }

    def _cache_subsystem_content(self, path: Path, content: str):
        """Cache subsystem content."""
        subsystem = path.parent.name
        sections = self._extract_sections(content)
        self.documentation_cache[f"subsystem_{subsystem}"] = {
            "content": content,
            "sections": sections
        }

    async def handle_list_tools(self) -> List[Tool]:
        """Handle list_tools request."""
        logger.debug("Listing tools")
        tools = []

        # Add overview tool
        tools.append(Tool(
            name="truenas_overview",
            description="Get an overview of the TrueNAS middleware architecture and repository structure",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ))

        # Add plugin documentation tool
        tools.append(Tool(
            name="truenas_plugin_docs",
            description="Get documentation for TrueNAS plugins (service types, patterns, specific plugins)",
            inputSchema={
                "type": "object",
                "properties": {
                    "plugin_name": {
                        "type": "string",
                        "description": "Name of a specific plugin (e.g., 'smb', 'apps', 'certificate'). Leave empty for general plugin documentation."
                    },
                    "topic": {
                        "type": "string",
                        "enum": ["service_types", "patterns", "categories", "all"],
                        "description": "Specific topic to retrieve. Use 'all' for complete documentation."
                    }
                },
                "required": []
            }
        ))

        # Add API documentation tool
        tools.append(Tool(
            name="truenas_api_docs",
            description="Get API documentation (versioning, models, patterns, best practices)",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["versioning", "models", "patterns", "best_practices", "all"],
                        "description": "Specific API topic to retrieve"
                    }
                },
                "required": []
            }
        ))

        # Add testing documentation tool
        tools.append(Tool(
            name="truenas_testing_docs",
            description="Get testing documentation and patterns for TrueNAS integration tests",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["overview", "patterns", "all"],
                        "description": "Testing topic to retrieve"
                    }
                },
                "required": []
            }
        ))

        # Add subsystem documentation tool
        tools.append(Tool(
            name="truenas_subsystem_docs",
            description="Get documentation for specific TrueNAS subsystems (alert, alembic, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "subsystem": {
                        "type": "string",
                        "description": "Name of the subsystem (e.g., 'alert', 'alembic')"
                    }
                },
                "required": ["subsystem"]
            }
        ))

        # Add search tool
        tools.append(Tool(
            name="truenas_search_docs",
            description="Search across all TrueNAS documentation for specific keywords or topics",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords, method names, concepts)"
                    }
                },
                "required": ["query"]
            }
        ))

        # Add test running tool
        tools.append(Tool(
            name="truenas_run_tests",
            description="Run TrueNAS middleware tests using Docker. Can run all tests or specific test files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to middleware repository (default: /Users/waqar/Desktop/work/ixsystems/codes/middleware)"
                    },
                    "test_file": {
                        "type": "string",
                        "description": "Specific test file to run (e.g., test_construct_schema.py)"
                    }
                },
                "required": []
            }
        ))

        logger.debug(f"Returning {len(tools)} tools")
        return tools

    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls."""
        logger.debug(f"Calling tool: {name} with arguments: {arguments}")

        try:
            if name == "truenas_overview":
                return await self._handle_overview_tool()
            elif name == "truenas_plugin_docs":
                return await self._handle_plugin_docs_tool(arguments)
            elif name == "truenas_api_docs":
                return await self._handle_api_docs_tool(arguments)
            elif name == "truenas_testing_docs":
                return await self._handle_testing_docs_tool(arguments)
            elif name == "truenas_subsystem_docs":
                return await self._handle_subsystem_docs_tool(arguments)
            elif name == "truenas_search_docs":
                return await self._handle_search_docs_tool(arguments)
            elif name == "truenas_run_tests":
                return await self._handle_run_tests_tool(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            logger.error(f"Error handling tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_overview_tool(self) -> List[TextContent]:
        """Handle overview tool call."""
        if "overview" in self.documentation_cache:
            content = self.documentation_cache["overview"]["content"]
            sections = self.documentation_cache["overview"]["sections"]
            
            if "Development Guidelines" in sections:
                content += "\n\n## Development Guidelines\n" + sections["Development Guidelines"]
            
            return [TextContent(type="text", text=content)]
        return [TextContent(type="text", text="Overview documentation not found")]

    async def _handle_plugin_docs_tool(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle plugin documentation tool call."""
        plugin_name = arguments.get("plugin_name", "").strip()
        topic = arguments.get("topic", "all")

        # If specific plugin requested
        if plugin_name:
            cache_key = f"plugin_{plugin_name}"
            if cache_key in self.documentation_cache:
                content = self.documentation_cache[cache_key]["content"]
                return [TextContent(type="text", text=content)]
            else:
                # List available plugins
                available = [k.replace("plugin_", "") for k in self.documentation_cache.keys() if k.startswith("plugin_") and k != "plugins_overview"]
                return [TextContent(type="text", text=f"Plugin '{plugin_name}' not found. Available plugins: {', '.join(available)}")]

        # General plugin documentation
        if "plugins_overview" not in self.documentation_cache:
            return [TextContent(type="text", text="Plugin overview documentation not found")]

        sections = self.documentation_cache["plugins_overview"]["sections"]
        content_parts = []

        if topic == "all":
            content_parts.append(self.documentation_cache["plugins_overview"]["content"])
        elif topic == "service_types" and "Service Types and Base Classes" in sections:
            content_parts.append("## Service Types and Base Classes\n" + sections["Service Types and Base Classes"])
        elif topic == "patterns" and "Common Plugin Patterns" in sections:
            content_parts.append("## Common Plugin Patterns\n" + sections["Common Plugin Patterns"])
        elif topic == "categories" and "Key Plugins by Category" in sections:
            content_parts.append("## Key Plugins by Category\n" + sections["Key Plugins by Category"])

        if content_parts:
            return [TextContent(type="text", text="\n\n".join(content_parts))]
        else:
            return [TextContent(type="text", text=f"Topic '{topic}' not found in plugin documentation")]

    async def _handle_api_docs_tool(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle API documentation tool call."""
        topic = arguments.get("topic", "all")

        if "api" not in self.documentation_cache:
            return [TextContent(type="text", text="API documentation not found")]

        sections = self.documentation_cache["api"]["sections"]
        content_parts = []

        if topic == "all":
            content_parts.append(self.documentation_cache["api"]["content"])
        elif topic == "versioning":
            for key in ["Overview", "Directory Structure", "Migration Between Versions"]:
                if key in sections:
                    content_parts.append(f"## {key}\n{sections[key]}")
        elif topic == "models" and "Key Concepts" in sections:
            content_parts.append("## API Models and Concepts\n" + sections["Key Concepts"])
        elif topic == "patterns" and "Common Patterns" in sections:
            content_parts.append("## Common API Patterns\n" + sections["Common Patterns"])
        elif topic == "best_practices" and "Best Practices" in sections:
            content_parts.append("## API Best Practices\n" + sections["Best Practices"])

        if content_parts:
            return [TextContent(type="text", text="\n\n".join(content_parts))]
        else:
            return [TextContent(type="text", text=f"Topic '{topic}' not found in API documentation")]

    async def _handle_testing_docs_tool(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle testing documentation tool call."""
        topic = arguments.get("topic", "all")

        if "testing" not in self.documentation_cache:
            return [TextContent(type="text", text="Testing documentation not found")]

        sections = self.documentation_cache["testing"]["sections"]
        content_parts = []

        if topic == "all":
            content_parts.append(self.documentation_cache["testing"]["content"])
        elif topic == "overview":
            for key in ["Overview", "Test Structure", "Writing Tests"]:
                if key in sections:
                    content_parts.append(f"## {key}\n{sections[key]}")
        elif topic == "patterns" and "Common Patterns" in sections:
            content_parts.append("## Testing Patterns\n" + sections["Common Patterns"])

        if content_parts:
            return [TextContent(type="text", text="\n\n".join(content_parts))]
        else:
            return [TextContent(type="text", text=f"Topic '{topic}' not found in testing documentation")]

    async def _handle_subsystem_docs_tool(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle subsystem documentation tool call."""
        subsystem = arguments.get("subsystem", "").strip()
        
        if not subsystem:
            # List available subsystems
            available = [k.replace("subsystem_", "") for k in self.documentation_cache.keys() if k.startswith("subsystem_")]
            return [TextContent(type="text", text=f"Please specify a subsystem. Available: {', '.join(available)}")]

        cache_key = f"subsystem_{subsystem}"
        if cache_key in self.documentation_cache:
            content = self.documentation_cache[cache_key]["content"]
            return [TextContent(type="text", text=content)]
        else:
            available = [k.replace("subsystem_", "") for k in self.documentation_cache.keys() if k.startswith("subsystem_")]
            return [TextContent(type="text", text=f"Subsystem '{subsystem}' not found. Available subsystems: {', '.join(available)}")]

    async def _handle_search_docs_tool(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search documentation tool call."""
        query = arguments.get("query", "").strip().lower()
        
        if not query:
            return [TextContent(type="text", text="Please provide a search query")]

        results = []
        
        # Search through all cached documentation
        for doc_key, doc_data in self.documentation_cache.items():
            content = doc_data["content"].lower()
            sections = doc_data.get("sections", {})
            
            # Search in content
            if query in content:
                # Find context around the match
                lines = doc_data["content"].split('\n')
                matching_lines = []
                
                for i, line in enumerate(lines):
                    if query in line.lower():
                        # Get surrounding context
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = '\n'.join(lines[start:end])
                        matching_lines.append(f"...{context}...")
                
                doc_type = doc_key.replace("_", " ").title()
                results.append(f"## Found in {doc_type}\n\n" + '\n\n'.join(matching_lines[:3]))  # Limit matches per doc

        if results:
            return [TextContent(type="text", text=f"# Search Results for '{query}'\n\n" + '\n\n---\n\n'.join(results))]
        else:
            return [TextContent(type="text", text=f"No results found for '{query}'")]

    async def _handle_run_tests_tool(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle running middleware tests."""
        repo_path = arguments.get("repo_path", "/Users/waqar/Desktop/work/ixsystems/codes/middleware")
        test_file = arguments.get("test_file", "")
        
        # Path to the test script
        script_path = Path(__file__).parent / "run_middleware_tests.sh"
        
        if not script_path.exists():
            return [TextContent(type="text", text=f"Test script not found at {script_path}")]
        
        # Build command
        cmd = [str(script_path), repo_path]
        if test_file:
            cmd.append(test_file)
        
        logger.info(f"Running test command: {' '.join(cmd)}")
        
        try:
            # Run the test script with a timeout (10 minutes for tests)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=600  # 10 minutes
            )
            
            # Decode output
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            # Format result
            result_parts = []
            
            if process.returncode == 0:
                result_parts.append("✅ Tests completed successfully!")
            else:
                result_parts.append(f"❌ Tests failed with exit code: {process.returncode}")
            
            # Add output
            if stdout_str:
                # Extract key information from output
                lines = stdout_str.split('\n')
                
                # Look for test results
                test_output = []
                capture = False
                for line in lines:
                    if "test session starts" in line:
                        capture = True
                    if capture:
                        test_output.append(line)
                    if "passed" in line and "warnings" in line:
                        capture = False
                        test_output.append(line)
                        break
                
                if test_output:
                    result_parts.append("\n## Test Output\n```\n" + "\n".join(test_output) + "\n```")
                else:
                    # If no pytest output found, show last 50 lines
                    result_parts.append("\n## Output (last 50 lines)\n```\n" + "\n".join(lines[-50:]) + "\n```")
            
            if stderr_str and process.returncode != 0:
                result_parts.append(f"\n## Errors\n```\n{stderr_str}\n```")
            
            return [TextContent(type="text", text="\n".join(result_parts))]
            
        except asyncio.TimeoutError:
            return [TextContent(type="text", text="❌ Test execution timed out after 10 minutes")]
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return [TextContent(type="text", text=f"❌ Error running tests: {str(e)}")]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            initialization_options = self.server.create_initialization_options()
            await self.server.run(
                read_stream,
                write_stream,
                initialization_options,
                raise_exceptions=True
            )


async def main():
    """Main entry point."""
    # Create and run server with default docs directory
    doc_server = TrueNASDocToolsServer()
    await doc_server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())