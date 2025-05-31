# Plugin Documentation Template

Use this template when creating new CLAUDE.md files for TrueNAS middleware plugins.

```markdown
# [Plugin Name] Plugin

## Overview
[Brief description of what the plugin does and its primary purpose]

## Architecture

### Service Structure
- **[ServiceName]** ([BaseClass]) - [Purpose]
- **[ServiceName2]** ([BaseClass]) - [Purpose]

### Data Model
- [Describe how data is stored]
- [Key database tables/models]
- [Relationships between entities]

## Core Concepts

### [Concept 1]
[Explain important concept]

### [Concept 2]
[Explain another concept]

## Key Methods

### [Category 1]
- `service.method1` - [What it does]
- `service.method2` - [What it does]

### [Category 2]
- `service.method3` - [What it does]
- `service.method4` - [What it does]

## Common Patterns

### [Pattern Name]
```python
# Pseudo-code showing the pattern
@api_method(InputArgs, OutputResult)
async def method_name(self, data):
    # Step 1: Validation
    # Step 2: Business logic
    # Step 3: Database operation
    # Step 4: Post-processing
    # Return result
```

### [Another Pattern]
[Describe the pattern and when to use it]

## Integration Points

### [Related Service 1]
- [How they interact]
- [What methods are called]
- [Data flow between services]

### [Related Service 2]
- [Integration details]

## API Patterns

### [Operation Type]
- [Key considerations]
- [Input validation rules]
- [Output format]
- [Error handling]

## Security Considerations

### [Security Aspect 1]
- [What to consider]
- [Best practices]

### [Security Aspect 2]
- [Security measures]

## Testing Approach

### Unit Tests
- [What to test]
- [Key test scenarios]

### Integration Tests
- [End-to-end scenarios]
- [Service interaction tests]

## Troubleshooting

### Common Issues

1. **[Issue Name]**
   - [Symptoms]
   - [Root cause]
   - [Solution]

2. **[Another Issue]**
   - [Details]

### Debug Tools
- `service.debug_method` - [What it shows]
- `service.validate` - [What it checks]

## Best Practices

### [Category]
1. [Best practice 1]
2. [Best practice 2]

### [Another Category]
1. [Best practice 3]
2. [Best practice 4]
```

## Guidelines for Using This Template

1. **Keep It Concise**: Each section should be informative but not verbose
2. **Focus on Patterns**: Emphasize reusable patterns over specific implementations
3. **Include Integration**: Always document how the plugin interacts with others
4. **Add Examples**: Use pseudo-code to illustrate concepts
5. **Think About Users**: What would a developer need to know to work with this plugin?

## Section Explanations

- **Overview**: One paragraph explaining the plugin's purpose
- **Architecture**: High-level design decisions and structure
- **Core Concepts**: Domain-specific concepts users must understand
- **Key Methods**: Most important API methods grouped by functionality
- **Common Patterns**: Reusable code patterns with examples
- **Integration Points**: How this plugin connects with others
- **API Patterns**: Request/response patterns and validation rules
- **Security**: Security considerations specific to this plugin
- **Testing**: How to test this plugin effectively
- **Troubleshooting**: Common problems and solutions
- **Best Practices**: Recommendations for using the plugin

## What NOT to Include

- ❌ Full source code implementations
- ❌ Detailed parameter lists (these are in API docs)
- ❌ Version-specific details
- ❌ Internal implementation details
- ❌ Debugging information that changes frequently

## Examples of Good Documentation

### Good Pattern Description
```markdown
### Validation Pattern
All input validation follows these steps:
1. Create ValidationErrors instance
2. Validate individual fields
3. Check business rules
4. Verify relationships with other entities
5. Call verrors.check() to raise if errors exist

This ensures consistent error messages and proper HTTP status codes.
```

### Good Integration Description
```markdown
### Storage Plugin Integration
- Uses `pool.dataset.query` to list available datasets
- Calls `pool.dataset.create` for new dataset creation
- Monitors space using `pool.get_disks`
- Integrates with snapshots via `zfs.snapshot.create`

Data flow: User request → Certificate plugin → Storage plugin → ZFS
```

Remember: The goal is to help developers understand the plugin's design and usage patterns, not to duplicate the source code.