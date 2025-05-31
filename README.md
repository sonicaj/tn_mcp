# TrueNAS Middleware MCP Server

This MCP (Model Context Protocol) server provides optimized documentation resources from the TrueNAS middleware repository to Code Claude, helping it understand the codebase structure and APIs without context overload.

## Quick Start

1. **For Code Claude Integration**: See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. **For Usage in Code Claude**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. **For Adding Documentation**: See [DOCUMENTATION_GUIDE.md](DOCUMENTATION_GUIDE.md)
4. **For Plugin Doc Template**: See [PLUGIN_DOCUMENTATION_TEMPLATE.md](PLUGIN_DOCUMENTATION_TEMPLATE.md)
5. **For Development Plans**: See [ACTION_PLAN.md](ACTION_PLAN.md)

## Features

- Automatically discovers and processes all CLAUDE.md files in the middleware repository
- Organizes documentation into logical categories (Overview, Plugins, API, Testing, Subsystems)
- Provides concise, focused resources to avoid context overload
- Implements intelligent content summarization

## Setup Options

### Option 1: Native Python (Recommended)

1. Create and activate the virtual environment:
```bash
python3.11 -m venv venv_tn_mcp
source venv_tn_mcp/bin/activate  # On Windows: venv_tn_mcp\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
./run_server.sh  # Or: python truenas_mcp_server.py
```

### Option 2: Docker Container

1. Build the Docker image:
```bash
docker-compose build
```

2. Run the server:
```bash
docker-compose run --rm truenas-mcp
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

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed setup instructions.

**Quick Config** (add to `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "truenas-docs": {
      "command": "/path/to/venv_tn_mcp/bin/python",
      "args": ["/path/to/tn_mcp/truenas_mcp_server.py"]
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