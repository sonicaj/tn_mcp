# Code Claude Integration Guide

This guide explains how to integrate the TrueNAS MCP tools server with Code Claude for seamless access to middleware documentation.

## Important: Tools vs Resources

Code Claude currently only supports MCP **tools**, not MCP resources. This server exposes documentation as tools that Code Claude can invoke directly.

## How Code Claude Uses MCP Servers

Code Claude integrates with MCP servers through its configuration file, typically located at:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## Integration Methods

### Method 1: Native Python Execution (Recommended)

This is the simplest approach for local development.

#### Setup Steps:

1. **Ensure Python 3.11+ is installed**
   ```bash
   python3.11 --version
   ```

2. **Clone and set up the MCP server**
   ```bash
   git clone <repository-url> /path/to/tn_mcp
   cd /path/to/tn_mcp
   python3.11 -m venv venv_tn_mcp
   source venv_tn_mcp/bin/activate  # On Windows: venv_tn_mcp\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Code Claude**
   
   Add to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "truenas-docs-tools": {
         "command": "/path/to/tn_mcp/run_mcp_tools_server.sh",
         "env": {
           "MCP_SERVER_MODE": "production"
         }
       }
     }
   }
   ```
   
   Alternative configuration using Python directly:
   ```json
   {
     "mcpServers": {
       "truenas-docs-tools": {
         "command": "/path/to/tn_mcp/venv_tn_mcp/bin/python",
         "args": ["/path/to/tn_mcp/truenas_mcp_tools_server.py"],
         "env": {
           "PYTHONPATH": "/path/to/tn_mcp",
           "MCP_SERVER_MODE": "production"
         }
       }
     }
   }
   ```

4. **Restart Code Claude** to load the new configuration

### Method 2: Docker Container (Isolated Environment)

For better isolation and consistency across different systems.

#### Advantages:
- No Python version conflicts
- Consistent environment
- Easy distribution
- Can be shared across team

#### Disadvantages:
- Requires Docker to be running
- Slightly more complex setup
- Small performance overhead

## Usage in Code Claude

Once configured, Code Claude can invoke the following TrueNAS documentation tools:

### 1. **Available Tools**
- **`truenas_overview`** - Get middleware architecture overview
- **`truenas_plugin_docs`** - Get plugin documentation (general or specific)
- **`truenas_api_docs`** - Get API documentation by topic
- **`truenas_testing_docs`** - Get testing documentation
- **`truenas_subsystem_docs`** - Get subsystem-specific docs
- **`truenas_search_docs`** - Search across all documentation

### 2. **Automatic Documentation Access**
When working on TrueNAS middleware code, Code Claude will automatically:
- Invoke relevant tools when you ask questions
- Provide context about specific plugins or APIs
- Help with code patterns and best practices

### 3. **Example Workflows**

**Example 1: Creating a new service**
```
User: "I need to create a new CRUD service for managing certificates"

Code Claude automatically invokes:
- truenas_plugin_docs(topic="service_types")
- truenas_plugin_docs(plugin_name="certificate")
- truenas_api_docs(topic="patterns")

Then provides:
- The correct base class to extend
- Example patterns from existing services
- Proper validation and error handling
```

**Example 2: Understanding a specific plugin**
```
User: "How does the SMB plugin work in TrueNAS?"

Code Claude automatically invokes:
- truenas_plugin_docs(plugin_name="smb")

Then explains:
- SMB plugin architecture
- Key methods and operations
- Integration with other services
```

## Verifying Integration

1. **Check MCP Server Status**
   In Code Claude, you should see "truenas-docs-tools" in the MCP servers list

2. **Test Tool Access**
   Ask Code Claude: "Get the TrueNAS middleware overview documentation"

3. **Verify Tool Functionality**
   Ask Code Claude: "Search TrueNAS docs for CRUD service patterns"

4. **List Available Tools**
   The server should expose 6 tools:
   - truenas_overview
   - truenas_plugin_docs
   - truenas_api_docs
   - truenas_testing_docs
   - truenas_subsystem_docs
   - truenas_search_docs

## Troubleshooting

### Server Not Appearing
1. Check the config file syntax (valid JSON)
2. Ensure paths are absolute, not relative
3. Verify Python executable path is correct
4. Check Code Claude logs for errors

### Resources Not Loading
1. Ensure docs/ directory contains CLAUDE.md files
2. Check file permissions
3. Run test_server.py to verify functionality
4. Check for Python import errors

### Performance Issues
1. The server pre-processes documentation on startup
2. First access might be slower
3. Consider reducing documentation size if needed

## Best Practices

1. **Keep Documentation Updated**
   - Regularly sync CLAUDE.md files from middleware repo
   - Update when new plugins or features are added

2. **Resource Usage**
   - Request specific resources rather than browsing all
   - Use the index resource to discover what's available
   - Combine related resources for complex tasks

3. **Development Workflow**
   - Start with overview resources for context
   - Use specific plugin docs when implementing
   - Reference API patterns for consistency

## Docker Implementation (If Needed)

If you prefer Docker isolation, here's what would be needed:

### Dockerfile Considerations:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "truenas_mcp_tools_server.py"]
```

### Docker Compose for Easy Management:
```yaml
version: '3.8'
services:
  truenas-mcp:
    build: .
    volumes:
      - ./docs:/app/docs:ro
    stdin_open: true
    tty: true
    environment:
      - MCP_SERVER_MODE=production
```

### Code Claude Config for Docker:
```json
{
  "mcpServers": {
    "truenas-docs-tools": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-v", "./docs:/app/docs:ro", "-e", "MCP_SERVER_MODE=production", "truenas-mcp"]
    }
  }
}
```

## Recommendation

For local development, **native Python execution is recommended** because:
1. Simpler setup and debugging
2. Better performance
3. Easier to modify and test
4. No Docker daemon requirement

Use Docker only if:
- You need strict environment isolation
- Sharing across multiple developers
- Deploying to a server environment
- Having Python version conflicts