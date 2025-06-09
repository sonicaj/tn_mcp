# Middlewared Package Overview

## Purpose
The middlewared package is the core of TrueNAS - it's the API server that boots up and handles all user requests, manages system services, and provides the interface between the frontend and the operating system.

## Directory Structure

### Core Components

- **`main.py`** - Entry point for the middleware daemon
- **`worker.py`** - Worker process management
- **`client/`** - Client libraries for connecting to middleware
- **`restful.py`** - REST API implementation
- **`job.py`** - Job management system for long-running operations
- **`event.py`** - Event system for real-time updates

### Key Directories

#### `/alembic/`
- Database schema migrations using Alembic
- Migrations follow naming: `YYYY-MM-DD_HH-MM_description.py`
- Each release (e.g., 25.10) has its own set of migrations
- Run with `alembic upgrade head`

#### `/alert/`
- Alert system implementation
- `base.py` - Base alert classes
- `source/` - Different alert sources (disk, certificate, replication, etc.)
- `service/` - Alert notification services (email, Slack, PagerDuty, etc.)

#### `/api/`
- API versioning and Pydantic models
- `current.py` - Points to the current API version
- `vYY_MM_X/` - Version-specific API definitions
- `base/` - Base classes and utilities for API models

#### `/plugins/`
- All service implementations (SSH, SMB, NFS, etc.)
- Each plugin extends base service classes
- Implements the business logic for TrueNAS features

#### `/etc_files/`
- System configuration file generators
- Python/Mako templates that generate config files
- Examples: `fstab.mako`, `smb4.conf.mako`, `exports.mako`

#### `/migration/`
- Data migrations (require middleware to be running)
- Different from alembic migrations (schema changes)
- Handle data transformation between versions

#### `/utils/`
- Utility functions used throughout middleware
- Examples: `crypto.py`, `network.py`, `privilege.py`

#### `/service/`
- Base service classes and decorators
- `base.py` - ServiceBase metaclass
- `service.py` - Base Service class
- `crud_service.py` - CRUD operations base
- `config_service.py` - Single config entity base

#### `/common/`
- Common functionality
- Attachment delegates for special field types
- Event source definitions

#### `/pytest/`
- Unit tests for middleware components
- Test utilities and helper functions

#### `/test/`
- Integration test utilities
- Helper functions for integration tests in `/tests/`

## Service Development

### Creating a New Service

1. Create a file in `/plugins/` directory
2. Define a model class (if using database)
3. Extend appropriate base class:
   ```python
   class MyService(CRUDService):
       class Config:
           datastore = 'my_table'
           datastore_prefix = 'my_'
   ```

### API Method Definition

Use the `@api_method` decorator with Pydantic models:
```python
@api_method(MyCreateArgs, MyCreateResult)
async def do_create(self, data):
    # Implementation
```

### Database Operations

- Use `middleware.call('datastore.query', 'table_name')`
- Automatic field prefix handling with `datastore_prefix`
- Support for relationships and extensions

## Key Concepts

### Jobs
- Long-running operations use the job system
- Decorate methods with `@job()`
- Provides progress tracking and cancellation

### Events
- Real-time updates through WebSocket
- Services can emit events for state changes
- Clients subscribe to specific event types

### Validation
- Input validation using Pydantic models
- `ValidationErrors` for detailed error reporting
- Schema validation at API boundaries

### Roles and Permissions
- Role-based access control (RBAC)
- Services define `role_prefix`
- Methods inherit permissions from service

## Development Tips

1. Always define Pydantic models for public API methods
2. Use appropriate base service class for your use case
3. Follow existing patterns in similar services
4. Add proper validation and error handling
5. Write unit tests in `/pytest/` for utilities
6. Integration tests go in repository root `/tests/`