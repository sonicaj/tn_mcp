# TrueNAS Middleware Development with MCP Documentation Server

This document should be placed at `/Users/waqar/Desktop/work/ixsystems/codes/middleware/CLAUDE.md` to guide developers on using the new MCP documentation server with Code Claude.

## Overview

The TrueNAS middleware repository now has an associated MCP (Model Context Protocol) server that provides optimized documentation access to Code Claude. This enables AI-assisted development with full context awareness of the middleware architecture, APIs, and patterns.

## MCP Server Integration

### What is the MCP Server?

The MCP server (`truenas-docs`) is a separate service that:
- Processes all CLAUDE.md documentation files in the middleware repository
- Provides structured, searchable documentation resources
- Optimizes content delivery to avoid AI context overload
- Enables Code Claude to understand the codebase architecture and patterns

### Available Resources

When working with Code Claude, you have access to these documentation resources:

- `truenas://overview` - High-level middleware architecture
- `truenas://development/guidelines` - Development best practices
- `truenas://plugins/service-types` - Guide to Service, ConfigService, CRUDService, SystemServiceService
- `truenas://plugins/patterns` - Common plugin implementation patterns
- `truenas://plugins/{name}` - Specific plugin documentation
- `truenas://api/versioning` - API versioning system
- `truenas://api/models` - Pydantic model patterns
- `truenas://testing/overview` - Testing guide
- `truenas://testing/patterns` - Testing patterns

## Development Workflows with Code Claude

### 1. Creating a New Plugin

When creating a new plugin, ask Code Claude:
```
"I need to create a new plugin for managing SSL certificates. It should support CRUD operations for certificates and integrate with the system's certificate store."
```

Code Claude will:
- Reference `truenas://plugins/service-types` to recommend the appropriate base class
- Use `truenas://plugins/patterns` to provide implementation examples
- Apply `truenas://api/models` for proper API model definitions
- Suggest testing approaches from `truenas://testing/patterns`

### 2. Adding API Endpoints

For adding new API endpoints:
```
"Add a new API endpoint to the certificate plugin for validating certificate chains"
```

Code Claude will:
- Reference existing patterns in the plugin
- Use `truenas://api/versioning` for proper versioning
- Apply `truenas://api/models` for request/response models
- Ensure consistency with middleware conventions

### 3. Writing Tests

When writing tests:
```
"Write integration tests for the certificate validation endpoint"
```

Code Claude will:
- Reference `truenas://testing/overview` for test structure
- Use `truenas://testing/patterns` for common test patterns
- Follow existing test conventions in the repository

### 4. Debugging and Understanding Code

For understanding existing functionality:
```
"Explain how the apps plugin manages Docker containers"
```

Code Claude will:
- Reference `truenas://plugins/apps` for apps-specific documentation
- Provide context from related subsystems
- Explain integration points with other services

## Best Practices for CLAUDE.md Files

When creating or updating CLAUDE.md documentation in this repository:

### 1. Structure Your Documentation

```markdown
# Component Name

## Overview
Brief description of what this component does and why it exists.

## Architecture
Key architectural decisions and design patterns used.

## Core Concepts
Important concepts that developers need to understand.

## API Reference
Key methods and their purposes (not full implementation).

## Common Patterns
Examples of how to use this component.

## Integration Points
How this component interacts with others.

## Troubleshooting
Common issues and solutions.
```

### 2. Focus on Intent, Not Implementation

❌ Don't include full code implementations
✅ Do explain what the code does and why

❌ Don't duplicate what's already in code comments
✅ Do provide architectural context and decisions

### 3. Keep Documentation Concise

The MCP server will summarize content to avoid context overload. Help it by:
- Using clear section headers
- Keeping explanations focused
- Highlighting key patterns and decisions
- Avoiding redundant information

### 4. Update Documentation with Code Changes

When making significant changes:
1. Update the relevant CLAUDE.md file
2. Run the MCP server locally to verify documentation appears correctly
3. Test with Code Claude to ensure the context is helpful

## Setting Up for Development

### 1. Ensure MCP Server is Configured

Code Claude should have the `truenas-docs` MCP server configured. Verify by asking:
```
"What TrueNAS documentation resources are available?"
```

### 2. Use Documentation Resources

When working on specific areas, request relevant documentation:
```
"Show me the plugin development patterns from truenas://plugins/patterns"
```

### 3. Combine with Code Context

Code Claude works best when combining documentation with actual code:
```
"Using the patterns from truenas://plugins/patterns, help me implement a new configuration service for SNMP settings"
```

## Common Development Scenarios

### Scenario 1: New Developer Onboarding

New developers can quickly understand the codebase:
```
"I'm new to TrueNAS middleware development. Give me an overview of the architecture and how to get started with plugin development."
```

### Scenario 2: Complex Feature Implementation

For complex features spanning multiple plugins:
```
"I need to implement quota management that integrates with the storage, user, and reporting plugins. Guide me through the implementation."
```

### Scenario 3: API Migration

When updating API versions:
```
"I need to migrate the storage API from v25.04 to v25.10. What's the process and what should I consider?"
```

### Scenario 4: Performance Optimization

For performance-related work:
```
"The user list endpoint is slow with many users. How can I optimize it following middleware patterns?"
```

## Maintaining Documentation Quality

### Regular Reviews

1. Review CLAUDE.md files when making significant changes
2. Ensure documentation reflects current architecture
3. Remove outdated information
4. Add new patterns as they emerge

### Documentation Testing

Test your documentation by:
1. Running the MCP server locally
2. Asking Code Claude questions about your component
3. Verifying the responses are accurate and helpful

### Feedback Loop

If Code Claude provides incorrect or outdated information:
1. Update the relevant CLAUDE.md file
2. Restart the MCP server
3. Verify the correction with Code Claude

## Tips for Effective AI-Assisted Development

### 1. Be Specific in Requests
- ❌ "Help me with storage"
- ✅ "Help me add a new ZFS dataset property to the storage plugin"

### 2. Reference Documentation Resources
- ❌ "Show me how to write tests"
- ✅ "Using truenas://testing/patterns, show me how to test a CRUD service"

### 3. Provide Context
- ❌ "Fix this error"
- ✅ "I'm getting a validation error in the user service when setting quotas. Here's the error: [error details]"

### 4. Iterate and Refine
- Start with high-level design questions
- Move to specific implementation details
- Request code review and optimization suggestions

## Conclusion

The MCP documentation server enhances TrueNAS middleware development by providing Code Claude with deep understanding of the codebase. By maintaining good documentation and using the available resources effectively, developers can significantly accelerate their development workflow while maintaining code quality and consistency.

Remember: The MCP server is a tool to augment your development process. It works best when combined with your domain knowledge and the actual code context.