# TrueNAS MCP Server - Quick Reference for Code Claude

## Available Resources

### Core Documentation
- `truenas://index` - Complete resource index
- `truenas://overview` - Middleware architecture overview
- `truenas://development/guidelines` - Development best practices

### Plugin Development
- `truenas://plugins/service-types` - Service, ConfigService, CRUDService, SystemServiceService
- `truenas://plugins/patterns` - Common implementation patterns
- `truenas://plugins/categories` - All plugins by category
- `truenas://plugins/{name}` - Specific plugin docs (e.g., `truenas://plugins/apps`)

### API Development
- `truenas://api/versioning` - API versioning system
- `truenas://api/models` - Pydantic model patterns

### Testing
- `truenas://testing/overview` - Testing guide
- `truenas://testing/patterns` - Common test patterns

### Subsystems
- `truenas://subsystems/{name}` - Specific subsystem docs

## Common Use Cases in Code Claude

### 1. Creating a New Service
```
"I need to create a new service for managing SSL certificates"
```
Code Claude will reference:
- `truenas://plugins/service-types` - Choose appropriate base class
- `truenas://plugins/patterns` - Implementation patterns
- `truenas://api/models` - API model definitions

### 2. Adding API Endpoints
```
"How do I add a new API endpoint to an existing service?"
```
Code Claude will reference:
- `truenas://api/models` - Model definition patterns
- `truenas://api/versioning` - Version management

### 3. Writing Tests
```
"I need to write integration tests for my new feature"
```
Code Claude will reference:
- `truenas://testing/overview` - Test structure
- `truenas://testing/patterns` - Common patterns

### 4. Understanding Existing Code
```
"Explain how the apps plugin works"
```
Code Claude will reference:
- `truenas://plugins/apps` - Apps plugin documentation

## Tips for Effective Usage

### Be Specific
- ❌ "Show me the documentation"
- ✅ "Show me how to create a CRUD service"

### Reference Resources Directly
- ❌ "What's in the plugin docs?"
- ✅ "Show me truenas://plugins/patterns"

### Combine Resources
- "I need to create a new SMB share endpoint" 
  - Code Claude will combine multiple relevant resources

### Ask for Examples
- "Show me an example from truenas://plugins/patterns for validation"

## Workflow Examples

### Starting a New Feature
1. "What's the overview of TrueNAS middleware?" → `truenas://overview`
2. "I need to add user quota management" → Reviews relevant plugins
3. "Show me CRUD service patterns" → `truenas://plugins/patterns`
4. "How do I define API models?" → `truenas://api/models`

### Debugging Existing Code
1. "How does the apps plugin work?" → `truenas://plugins/apps`
2. "Show me the service types" → `truenas://plugins/service-types`
3. "What are the testing patterns?" → `truenas://testing/patterns`

### API Development
1. "How does API versioning work?" → `truenas://api/versioning`
2. "Show me Pydantic model examples" → `truenas://api/models`
3. "What are the plugin categories?" → `truenas://plugins/categories`

## Resource Navigation

### Browse All Resources
Ask: "Show me the truenas documentation index"

### Search for Specific Topics
Ask: "Which truenas resource covers Docker?"

### Get Resource Details
Ask: "What's in truenas://plugins/apps?"

## Integration Verification

To verify the MCP server is working:
1. Ask: "List available truenas resources"
2. Ask: "Show me truenas://index"
3. Ask: "What plugin patterns are documented?"

## Troubleshooting in Code Claude

If resources aren't available:
1. Check MCP server status in Code Claude
2. Restart Code Claude after config changes
3. Verify with: "Are truenas docs available?"

## Best Practices

1. **Start Broad, Then Narrow**
   - First: Overview resources
   - Then: Specific plugin/API docs

2. **Use Index for Discovery**
   - "Show me truenas://index" to see all available resources

3. **Combine Multiple Resources**
   - Don't hesitate to ask for multiple related resources

4. **Keep Context Focused**
   - Request specific resources rather than all documentation