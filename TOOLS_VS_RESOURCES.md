# MCP Tools vs Resources for Code Claude

## The Issue

Code Claude currently only supports MCP **tools**, not MCP **resources**. This means:

- ❌ **Resources** (like `truenas://plugins/smb`) cannot be accessed by Code Claude
- ✅ **Tools** (like `truenas_plugin_docs`) can be invoked by Code Claude

## The Solution

We've created `truenas_mcp_tools_server.py` which exposes the same documentation as **tools** instead of resources.

### Available Tools

1. **`truenas_overview`** - Get TrueNAS middleware architecture overview
   ```json
   // No arguments needed
   {}
   ```

2. **`truenas_plugin_docs`** - Get plugin documentation
   ```json
   {
     "plugin_name": "smb",  // Optional: specific plugin
     "topic": "service_types"  // Optional: service_types, patterns, categories, all
   }
   ```

3. **`truenas_api_docs`** - Get API documentation
   ```json
   {
     "topic": "versioning"  // Optional: versioning, models, patterns, best_practices, all
   }
   ```

4. **`truenas_testing_docs`** - Get testing documentation
   ```json
   {
     "topic": "overview"  // Optional: overview, patterns, all
   }
   ```

5. **`truenas_subsystem_docs`** - Get subsystem documentation
   ```json
   {
     "subsystem": "alert"  // Required: subsystem name
   }
   ```

6. **`truenas_search_docs`** - Search all documentation
   ```json
   {
     "query": "CRUD"  // Required: search term
   }
   ```

## Usage in Code Claude

When Code Claude needs TrueNAS documentation, it can now invoke these tools:

```
User: "How do I create a CRUD service in TrueNAS?"

Code Claude will automatically invoke:
- truenas_plugin_docs(topic="service_types")
- truenas_search_docs(query="CRUD")
```

## Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "truenas-docs-tools": {
      "command": "python",
      "args": ["/path/to/truenas_mcp_tools_server.py"],
      "env": {
        "MCP_SERVER_MODE": "production"
      }
    }
  }
}
```

## Testing

Run the test script to verify the tools work:

```bash
python test_tools_server.py
```