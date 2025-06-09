# API Directory - Pydantic Models and Versioning

## Overview
This directory contains all API model definitions using Pydantic for type validation and API versioning support. Every public API method must use these models for input/output validation.

## Directory Structure

### `current.py`
- Imports from the latest API version
- Always points to the most recent version directory
- Services import models from here: `from middlewared.api import v1`

### Version Directories (`vYY_MM_X/`)
- Named by release version: `v25_04_0`, `v25_10_0`, etc.
- Each version can override specific models
- Inherits unchanged models from previous versions
- Contains `__init__.py` that manages imports

### `base/` Directory
Core utilities and base classes for API models:

- **`model.py`** - Base model classes and utilities
- **`decorator.py`** - The `@api_method` decorator
- **`types/`** - Custom Pydantic types
- **`validators.py`** - Common validators
- **`jsonschema.py`** - JSON schema generation

## Key Concepts

### 1. Base Model Classes

```python
from middlewared.api.base import BaseModel

class UserEntry(BaseModel):
    """Represents a user account"""
    id: int
    username: str
    uid: int
    # Fields with descriptions become API docs
```

### 2. CRUD Model Pattern

For each entity, typically define:

```python
# The main entry model
class UserEntry(BaseModel):
    id: int
    username: str
    uid: int
    shell: str
    # ... all fields

# Creation model (no id, no computed fields)
class UserCreate(UserEntry):
    id: Excluded = excluded_field()
    builtin: Excluded = excluded_field()

# Update model (all fields optional)
class UserUpdate(UserCreate, metaclass=ForUpdateMetaclass):
    pass

# Request/Response wrappers
UserCreateArgs = single_argument_args(UserCreate)
UserCreateResult = single_argument_result(UserEntry)
UserUpdateArgs = single_argument_args(UserUpdate)
UserUpdateResult = single_argument_result(UserEntry)
```

### 3. Special Types and Fields

```python
# Secret fields (hidden in logs)
password: Secret[str]

# Optional fields
email: str | None

# Fields with validation
port: int = Field(ge=1, le=65535)

# Excluded from create/update
id: Excluded = excluded_field()

# Non-empty strings
name: NonEmptyString

# Union types for flexibility
username: LocalUsername | RemoteUsername
```

### 4. API Method Usage

In plugins, use models with `@api_method`:

```python
from middlewared.api import v1

@api_method(v1.UserCreateArgs, v1.UserCreateResult, roles=['ACCOUNT_WRITE'])
async def do_create(self, data):
    # data is already validated against UserCreate model
    # return value must match UserEntry model
```

### 5. Version Migration

Models can define migration methods:

```python
class UserEntry(BaseModel):
    # ... fields ...
    
    @classmethod
    def from_previous(cls, value, ctx):
        # Convert from previous version
        if 'old_field' in value:
            value['new_field'] = value.pop('old_field')
        return value
    
    def to_previous(self, ctx):
        # Convert to previous version
        value = self.model_dump()
        if 'new_field' in value:
            value['old_field'] = value.pop('new_field')
        return value
```

## Best Practices

### 1. Model Organization
- One file per service/entity type
- Group related models together
- Use clear, descriptive names

### 2. Documentation
- Add docstrings to models and fields
- These become API documentation
- Include examples where helpful

### 3. Validation
- Use Pydantic validators for complex rules
- Prefer field-level validation
- Clear error messages

### 4. Backwards Compatibility
- Don't remove fields in same version
- Use deprecation warnings
- Provide migration methods

### 5. Type Safety
- Use specific types over generic ones
- Define custom types for common patterns
- Avoid `Any` type

## Common Patterns

### Query Models
```python
class UserQueryOptions(QueryOptions):
    extra_fields: list[Literal['groups']] = []

UserQueryArgs = single_argument_args(QueryArgs)
UserQueryResult = query_result(UserEntry)
```

### Nested Models
```python
class ShareEntry(BaseModel):
    path: str
    acl: AclEntry  # Nested model
    
class AclEntry(BaseModel):
    owner: str
    group: str
    mode: str
```

### Enums
```python
class ServiceState(enum.Enum):
    STARTED = "STARTED"
    STOPPED = "STOPPED"
    
class ServiceEntry(BaseModel):
    state: ServiceState
```

## Adding New API Models

1. Create model file in current version directory
2. Define Pydantic models following patterns
3. Export from `__init__.py`
4. Update `current.py` if needed
5. Use in plugin with `@api_method`
6. Add tests for validation

## Migration Between Versions

When creating a new API version:

1. Create new version directory
2. Copy `__init__.py` template
3. Override only changed models
4. Implement migration methods
5. Update `current.py` imports
6. Test compatibility thoroughly