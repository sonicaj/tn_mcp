# TrueNAS Middleware Documentation Guide

This guide explains how to document TrueNAS middleware plugins in this repository for optimal use with Code Claude through the MCP tools server.

## Overview

The MCP tools server approach provides several advantages over a single CLAUDE.md file in the middleware repository:

1. **No Context Overload**: Documentation is served on-demand through specific tools
2. **Better Organization**: Documentation is categorized and searchable
3. **Easier Maintenance**: Update docs without modifying the main middleware repo
4. **Version Control**: Documentation changes are tracked separately
5. **Code Claude Compatible**: Uses MCP tools that Code Claude can invoke directly

## How Documentation is Exposed to Code Claude

The MCP tools server exposes documentation through the following tools that Code Claude can invoke:

1. **`truenas_overview`** - Returns middleware architecture overview
2. **`truenas_plugin_docs`** - Returns plugin documentation (general or specific)
   - Parameters: `plugin_name` (optional), `topic` (optional)
3. **`truenas_api_docs`** - Returns API documentation by topic
   - Parameters: `topic` (versioning, models, patterns, best_practices, all)
4. **`truenas_testing_docs`** - Returns testing documentation
   - Parameters: `topic` (overview, patterns, all)
5. **`truenas_subsystem_docs`** - Returns subsystem-specific docs
   - Parameters: `subsystem` (required)
6. **`truenas_search_docs`** - Searches across all documentation
   - Parameters: `query` (required)

When Code Claude needs information about TrueNAS, it automatically invokes these tools to get the relevant documentation.

## Do You Still Need CLAUDE.md in Middleware?

**Short answer: No, you don't need CLAUDE.md files in the middleware repository if using this MCP server.**

However, you might want to keep a minimal CLAUDE.md in the middleware root that simply points to this MCP server:

```markdown
# TrueNAS Middleware

This repository uses an MCP documentation server for Code Claude integration.
Configure the `truenas-docs-tools` MCP server in Code Claude for full documentation access.

See: https://github.com/[your-org]/tn_mcp for setup instructions.
```

## Adding Documentation for Plugins

### 1. Documentation Structure

Place documentation files in the `docs/` directory following the middleware structure:

```
docs/
├── CLAUDE.md                                    # Root overview
├── src/
│   └── middlewared/
│       ├── CLAUDE.md                           # Middlewared overview
│       └── middlewared/
│           ├── plugins/
│           │   ├── CLAUDE.md                   # General plugins guide
│           │   ├── {plugin_name}/
│           │   │   └── CLAUDE.md              # Specific plugin docs
│           │   └── ...
│           ├── api/
│           │   └── CLAUDE.md                   # API documentation
│           └── ...
└── tests/
    └── CLAUDE.md                               # Testing documentation
```

### 2. How Documentation Access Works

When you add documentation for a plugin (e.g., `backup`):

1. **File Location**: `docs/src/middlewared/middlewared/plugins/backup/CLAUDE.md`
2. **Server Processing**: The MCP tools server finds and caches this content
3. **Tool Access**: Available via `truenas_plugin_docs(plugin_name="backup")`
4. **Code Claude Usage**: Automatically invoked when answering questions about backups

**Example Flow**:
```
User: "How do I implement a new backup provider?"
↓
Code Claude: truenas_plugin_docs(plugin_name="backup")
↓
Server: Returns backup plugin documentation
↓
Code Claude: Uses docs to provide accurate implementation guidance
```

### 3. Creating Plugin Documentation

#### Step 1: Create the Directory Structure

For a new plugin called `backup`:

```bash
mkdir -p docs/src/middlewared/middlewared/plugins/backup
```

#### Step 2: Create CLAUDE.md for the Plugin

Create `docs/src/middlewared/middlewared/plugins/backup/CLAUDE.md`:

```markdown
# Backup Plugin

## Overview
The backup plugin manages system configuration backups, including scheduled backups, 
cloud storage integration, and backup restoration.

## Architecture
- Extends ConfigService for backup settings
- Uses CRUDService for backup configurations
- Integrates with cloud storage providers (S3, B2, Google Drive)
- Implements job system for long-running operations

## Core Concepts

### Backup Types
1. **Configuration Backup**: System settings and database
2. **Data Backup**: User-specified datasets
3. **Full System Backup**: Complete system state

### Storage Backends
- Local storage
- SSH/SFTP
- S3-compatible storage
- Cloud providers

## Key Components

### BackupService (ConfigService)
Main service for backup configuration:
- `backup.config()` - Get backup settings
- `backup.update()` - Update settings
- `backup.run()` - Trigger manual backup

### CloudCredentialService (CRUDService)
Manages cloud storage credentials:
- CRUD operations for credentials
- Credential validation
- Provider-specific settings

## API Patterns

### Creating a Backup Task
```python
@api_method(BackupTaskCreateArgs, BackupTaskCreateResult)
async def create_task(self, data):
    # Validates schedule, storage, datasets
    # Creates periodic task
    # Returns task configuration
```

### Running Backup
```python
@api_method(BackupRunArgs, JobId)
async def run(self, id):
    # Validates backup exists
    # Creates job
    # Executes backup process
    # Returns job ID for tracking
```

## Common Patterns

### Job Integration
Long-running backups use the job system:
- Progress reporting
- Cancellation support
- Error handling

### Validation
- Path validation for local storage
- Credential testing for cloud storage
- Dataset existence checks

## Integration Points

### Storage Plugin
- Dataset snapshots before backup
- Replication integration

### System Plugin  
- Configuration export
- Database dumps

### Alert Plugin
- Backup failure alerts
- Storage space warnings

## Testing Approach

### Unit Tests
- Credential validation
- Path manipulation
- Configuration merging

### Integration Tests
- Full backup/restore cycle
- Cloud provider integration
- Job cancellation

## Troubleshooting

### Common Issues
1. **Permission Denied**: Check dataset permissions
2. **Cloud Auth Failures**: Validate credentials
3. **Storage Full**: Monitor destination space

### Debug Commands
- Check backup status: `backup.query`
- View logs: `backup.get_logs`
- Test credentials: `backup.verify_credentials`
```

### 3. Documentation Best Practices

#### Focus on Architecture, Not Implementation

✅ **Good Example**:
```markdown
## Architecture
The service uses a two-phase commit pattern to ensure consistency:
1. Validate all operations
2. Execute atomically with rollback on failure
```

❌ **Bad Example**:
```markdown
## Code
def do_backup(self):
    for dataset in datasets:
        subprocess.run(['zfs', 'snapshot', dataset])
    # ... 50 lines of implementation
```

#### Include Integration Context

✅ **Good Example**:
```markdown
## Integration Points
- Uses `pool.dataset.query` to list available datasets
- Calls `system.general.config` for system settings
- Integrates with `alert.oneshot_create` for notifications
```

#### Provide Pattern Examples

✅ **Good Example**:
```markdown
## Validation Pattern
All input validation follows this pattern:
1. Create ValidationErrors instance
2. Check each field with specific rules
3. Verify cross-field dependencies
4. Call verrors.check() to raise if errors exist
```

### 4. Updating the MCP Server

After adding new documentation:

1. **Test Locally**:
```bash
cd /path/to/tn_mcp
python test_server.py
```

2. **Verify Resources**:
```python
# In test_server.py or interactive Python
server = TrueNASDocServer()
resources = await server.handle_list_resources()
print([str(r.uri) for r in resources if 'backup' in str(r.uri)])
```

3. **Check Content**:
```python
content = await server.handle_read_resource("truenas://plugins/backup")
print(content[:500])  # Preview
```

### 5. Advanced Documentation Features

#### Cross-References

Link between related documentation:

```markdown
## Related Documentation
- See `truenas://plugins/alert` for alert integration
- See `truenas://api/models` for model patterns
- See `truenas://plugins/categories` for plugin overview
```

#### Code Examples

Include minimal, focused examples:

```markdown
## Usage Example
To create a backup configuration:
- Define backup schedule using cron syntax
- Specify datasets to include
- Configure storage destination
- Set retention policy
```

#### Decision Records

Document important architectural decisions:

```markdown
## Design Decisions

### Why ConfigService for Main Settings?
Single configuration entity for global backup settings, while
individual backup tasks use CRUDService for multiple configurations.

### Why Separate Cloud Credentials?
Reusable across multiple services (backup, cloudsync, replication).
```

## Workflow for New Documentation

### 1. Identify What to Document

Ask yourself:
- What would a new developer need to know?
- What patterns are used repeatedly?
- What integrations are important?
- What are common pitfalls?

### 2. Create Documentation

```bash
# Create directory
mkdir -p docs/src/middlewared/middlewared/plugins/newplugin

# Create CLAUDE.md
cat > docs/src/middlewared/middlewared/plugins/newplugin/CLAUDE.md << 'EOF'
# NewPlugin Name

## Overview
Brief description...

## Architecture
Key design decisions...

## Core Concepts
Important concepts...

## Common Patterns
Reusable patterns...

## Integration Points
How it connects to other plugins...

## Troubleshooting
Common issues and solutions...
EOF
```

### 3. Test with Code Claude

Once documentation is added, Code Claude will automatically access it when needed. For example:

**User asks**: "How do I create a backup task in TrueNAS?"

**Code Claude will**:
1. Invoke `truenas_plugin_docs(plugin_name="backup")` to get backup plugin documentation
2. Use the returned documentation to provide accurate guidance

**Manual testing**:
You can also explicitly ask Code Claude to retrieve documentation:
- "Get the backup plugin documentation from TrueNAS"
- "Search TrueNAS docs for backup patterns"
- "Show me the API documentation for TrueNAS"

### 4. Iterate

Based on Code Claude's responses:
- Add missing information
- Clarify confusing sections
- Add more examples if needed

## Benefits Over Single CLAUDE.md

### 1. Scalability
- Thousands of lines of docs without overwhelming context
- Load only what's needed for current task

### 2. Organization
- Logical structure matching code layout
- Easy to find and update specific docs

### 3. Searchability
- Code Claude can query specific topics
- Better resource discovery

### 4. Maintainability
- Update docs without touching main repo
- Track doc changes separately
- Multiple contributors can work on different sections

### 5. Performance
- Faster Code Claude responses
- No context window waste
- Optimized content delivery

## Migration from Existing CLAUDE.md

If you have existing CLAUDE.md files in middleware:

1. **Copy Structure**:
```bash
# Copy all CLAUDE.md files preserving structure
find /path/to/middleware -name "CLAUDE.md" -exec cp --parents {} docs/ \;
```

2. **Review and Optimize**:
- Remove implementation details
- Focus on patterns and architecture
- Add integration information

3. **Test Resources**:
- Ensure all resources load correctly
- Verify content is accessible
- Check for broken references

## Summary

Using this MCP server approach:
- ✅ No need for CLAUDE.md in middleware repository
- ✅ Better organization and maintenance
- ✅ Optimized for Code Claude's context window
- ✅ Easier to scale documentation
- ✅ Separate version control for docs

The MCP server transforms documentation from a monolithic file into a queryable knowledge base, making Code Claude more effective at understanding and working with the TrueNAS middleware codebase.