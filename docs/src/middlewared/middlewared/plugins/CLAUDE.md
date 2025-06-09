# Middleware Plugins Directory

## Overview
This directory contains all the service implementations that make up TrueNAS functionality. Each plugin is a Python module that extends one of the base service classes to provide specific features.

## Service Types and Base Classes

### 1. **Service** (Basic Service)
- Most basic service type
- No built-in CRUD operations
- Used for utility services or custom implementations
- Example: `service.py`, `zettarepl.py`

### 2. **ConfigService** (Single Configuration)
- Manages a single configuration entity
- Provides `config()` and `update()` methods
- Used for system-wide settings
- Examples: `ssh.py`, `ftp.py`, `mail.py`, `ntp.py`

### 3. **CRUDService** (Collection Management)
- Full Create, Read, Update, Delete operations
- Manages collections of entities
- Automatic event generation for changes
- Examples: `account.py` (users), `smb.py` (shares), `pool.py`

### 4. **SystemServiceService** (System Daemons)
- Extends ConfigService
- Integrates with systemd service management
- Provides start/stop/restart functionality
- Examples: `ssh.py`, `ftp.py`, `nfs.py`

## Common Plugin Patterns

### Model Definition
```python
class UserModel(sa.Model):
    __tablename__ = 'account_bsdusers'
    
    id = sa.Column(sa.Integer(), primary_key=True)
    bsdusr_username = sa.Column(sa.String(32))
    bsdusr_uid = sa.Column(sa.Integer())
    # ... more fields
```

### Service Configuration
```python
class UserService(CRUDService):
    class Config:
        datastore = 'account.bsdusers'
        datastore_prefix = 'bsdusr_'
        datastore_extend = 'user.extend'
        cli_namespace = 'account.user'
        role_prefix = 'ACCOUNT'
        entry = UserEntry  # Pydantic model
```

### API Method Pattern
```python
@api_method(UserCreateArgs, UserCreateResult, roles=['ACCOUNT_WRITE'])
async def do_create(self, data):
    # Validation
    verrors = ValidationErrors()
    if await self.middleware.call('user.query', [['username', '=', data['username']]]):
        verrors.add('username', 'User already exists')
    verrors.check()
    
    # Business logic
    # ...
    
    # Database operation
    user_id = await self.middleware.call('datastore.insert', 'account.bsdusers', user_data)
    
    # Post-processing
    await self._sync_cache()
    
    return await self.get_instance(user_id)
```

## Key Plugins by Category

### System Configuration
- **boot.py** - Boot environment management
- **config.py** - System configuration backup/restore
- **etc.py** - System file management
- **tunables.py** - Kernel tunables and sysctl

### Storage
- **pool.py** - ZFS pool management
- **zfs.py** - ZFS dataset operations
- **disk.py** - Disk management and info
- **filesystem.py** - File operations

### Networking
- **network.py** - Network interfaces and configuration
- **dns.py** - DNS client configuration
- **route.py** - Static routes
- **failover.py** - High availability

### Sharing Protocols
- **smb.py** - SMB/CIFS shares
- **nfs.py** - NFS exports
- **iscsi_*.py** - iSCSI targets and configuration
- **ftp.py** - FTP service

### Directory Services
- **activedirectory.py** - Active Directory integration
- **ldap.py** - LDAP client configuration
- **kerberos.py** - Kerberos realm management
- **idmap.py** - ID mapping configuration

### Services
- **ssh.py** - SSH daemon configuration
- **service.py** - Service management
- **cron.py** - Scheduled tasks
- **init_shutdown_script.py** - Startup/shutdown scripts

### Accounts
- **account.py** - User management (users and groups)
- **auth.py** - Authentication and sessions
- **privilege.py** - Roles and permissions

### System Management
- **update.py** - System updates
- **alert.py** - Alert configuration
- **support.py** - Support and debug info
- **reporting.py** - System statistics

## Plugin Development Guidelines

### 1. Validation
- Always validate input using `ValidationErrors`
- Check for conflicts and dependencies
- Provide clear error messages

### 2. Database Operations
- Use middleware datastore calls
- Respect transactions when needed
- Handle relationships properly

### 3. Events
- Emit appropriate events for state changes
- Use standard event names (entity.query)
- Include relevant data in events

### 4. Error Handling
- Raise `CallError` for operational errors
- Use appropriate error codes (errno)
- Log errors for debugging

### 5. Async Best Practices
- Use `async`/`await` for I/O operations
- Don't block the event loop
- Use `asyncio.gather` for parallel operations

### 6. Security
- Check permissions with role decorators
- Sanitize file paths and inputs
- Never expose sensitive data in logs

## Testing Plugins
- Unit tests: Create in `/middlewared/pytest/unit/plugins/`
- Integration tests: Add to `/tests/api2/`
- Mock external dependencies when needed
- Test error conditions and edge cases