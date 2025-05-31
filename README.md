# TrueNAS Middleware MCP Server

This MCP (Model Context Protocol) server provides optimized documentation resources from the TrueNAS middleware repository to Code Claude, helping it understand the codebase structure and APIs without context overload.

## Features

- Automatically discovers and processes all CLAUDE.md files in the middleware repository
- Organizes documentation into logical categories (Overview, Plugins, API, Testing, Subsystems)
- Provides concise, focused resources to avoid context overload
- Implements intelligent content summarization

## Setup

1. Create and activate the virtual environment:
```bash
python3.11 -m venv /Users/waqar/Desktop/work/ixsystems/codes/venv_tn_mcp
source /Users/waqar/Desktop/work/ixsystems/codes/venv_tn_mcp/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
source /Users/waqar/Desktop/work/ixsystems/codes/venv_tn_mcp/bin/activate
python truenas_mcp_server.py
```

## Available Resources

The server provides the following types of resources:

### Overview Resources
- `truenas://overview` - High-level middleware architecture
- `truenas://development/guidelines` - Development best practices

### Plugin Resources
- `truenas://plugins/service-types` - Guide to service base classes
- `truenas://plugins/patterns` - Common plugin patterns
- `truenas://plugins/categories` - Categorized plugin list
- `truenas://plugins/{plugin_name}` - Specific plugin documentation

### API Resources
- `truenas://api/versioning` - API versioning guide
- `truenas://api/models` - Pydantic model patterns

### Testing Resources
- `truenas://testing/overview` - Testing guide
- `truenas://testing/patterns` - Common testing patterns

### Subsystem Resources
- `truenas://subsystems/{name}` - Documentation for specific subsystems

## Integration with Code Claude

To use this MCP server with Code Claude, add the following to your MCP configuration:

```json
{
  "servers": {
    "truenas-docs": {
      "command": "python",
      "args": ["/Users/waqar/Desktop/work/ixsystems/codes/tn_mcp/truenas_mcp_server.py"],
      "env": {
        "VIRTUAL_ENV": "/Users/waqar/Desktop/work/ixsystems/codes/venv_tn_mcp",
        "PATH": "/Users/waqar/Desktop/work/ixsystems/codes/venv_tn_mcp/bin:$PATH"
      }
    }
  }
}
```

## How It Works

1. The server scans the middleware repository for all CLAUDE.md files
2. Each file is processed and categorized based on its location
3. Content is intelligently summarized to reduce context size
4. Resources are exposed via MCP protocol for Code Claude to query

## Optimization Strategy

To avoid context overload, the server:
- Extracts key sections from documentation
- Limits code examples to essential ones
- Focuses on API signatures and patterns rather than full implementations
- Groups related information into logical resources