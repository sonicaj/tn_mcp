# Docker Plugin

## Overview
The Docker plugin manages Docker Engine on TrueNAS SCALE, providing ZFS-backed container storage with integrated state management, backup capabilities, and high availability support.

## Architecture

### Core Components

#### 1. **DockerService** (`update.py`)
Main configuration service for Docker setup.

**Key Responsibilities:**
- Configure which ZFS pool hosts Docker
- Manage Docker daemon configuration
- Handle pool migrations
- Configure networking (address pools, IPv6)
- NVIDIA GPU runtime support

**Configuration Example:**
```python
# Configure Docker on a pool
await client.call('docker.update', {
    'pool': 'tank',
    'enable_image_updates': True,
    'address_pools': [
        {'base': '172.17.0.0/16', 'size': 24}
    ]
})
```

#### 2. **DockerStateService** (`state_management.py`)
Manages Docker service lifecycle and state tracking.

**States:**
- `PENDING` - Initial/transitional state
- `RUNNING` - Docker active and healthy
- `INITIALIZING` - Service starting up
- `STOPPING` - Service shutting down
- `STOPPED` - Service inactive
- `UNCONFIGURED` - No pool configured
- `FAILED` - Service failed
- `MIGRATING` - Pool migration in progress

**State Flow:**
```
UNCONFIGURED -> INITIALIZING -> RUNNING
                     |              |
                     v              v
                  FAILED        STOPPING -> STOPPED
```

#### 3. **DockerFilesystemManageService** (`fs_manage.py`)
Handles ZFS dataset mounting and validation.

**Operations:**
- Mount Docker datasets at `/.ix-apps`
- Validate filesystem structure
- Handle mount/unmount during state changes

### ZFS Dataset Structure

```
{pool}/ix-apps/                    # Root dataset (mounted at /.ix-apps)
├── docker/                        # Docker data directory
├── app_configs/                   # Application configurations
├── app_mounts/                    # Application persistent storage
└── truenas_catalog/               # App catalog data
```

**Dataset Properties:**
```python
{
    'aclmode': 'discard',
    'acltype': 'posix',
    'atime': 'off',
    'encryption': 'off',
    'overlay': 'on',
    'mountpoint': '/.ix-apps'
}
```

### Key Services

#### **DockerSetupService** (`state_setup.py`)
Initial setup and validation:
- Creates required ZFS datasets
- Sets dataset properties
- Validates network configuration
- Checks for conflicts

#### **DockerBackupService** (`backup.py`)
Backup and restore functionality:
- Full state backup using ZFS snapshots
- Application configuration preservation
- Atomic restore operations

#### **DockerMigrateService** (`migrate.py`)
Pool migration capabilities:
- Move Docker to different pool
- Preserves all application data
- Rollback on failure

## Docker Daemon Configuration

Generated at `/etc/docker/daemon.json`:
```json
{
    "data-root": "/.ix-apps/docker",
    "storage-driver": "overlay2",
    "ipv6": true,
    "fixed-cidr-v6": "fd00::/64",
    "default-address-pools": [
        {"base": "172.17.0.0/16", "size": 24}
    ],
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime"
        }
    }
}
```

## Key Operations

### Pool Configuration
```python
# Set Docker pool
await client.call('docker.update', {'pool': 'tank'})

# Get current config
config = await client.call('docker.config')

# Check state
state = await client.call('docker.state')
```

### Pool Migration
```python
# Migrate to new pool
job_id = await client.call('docker.migrate', {
    'pool': 'new_pool'
})
```

### Backup Operations
```python
# Create backup
backup_path = await client.call('docker.backup', {
    'apps': ['app1', 'app2']
})

# Restore backup
await client.call('docker.restore_backup', {
    'backup_path': '/path/to/backup.tar'
})
```

## State Management

### State Validation
Before starting Docker, the plugin validates:
1. Pool is configured and imported
2. Required datasets exist
3. Filesystems are properly mounted
4. No conflicting directories at `/.ix-apps`
5. Network interfaces are available

### Event Broadcasting
State changes are broadcast via WebSocket:
```python
{
    'collection': 'docker.state',
    'msg': 'changed',
    'fields': {'state': 'RUNNING'}
}
```

## Integration Points

### Service Dependencies
- **Kubernetes**: Cannot run simultaneously
- **Networking**: Bridge interface validation
- **GPU**: NVIDIA runtime integration
- **HA/Failover**: State synchronization

### File Locations
- Docker root: `/.ix-apps/docker`
- Daemon config: `/etc/docker/daemon.json`
- Systemd service: `docker.service`

## Utilities (`state_utils.py`)

### Constants
```python
DOCKER_DATASET_NAME = 'ix-apps'
DOCKER_MOUNTPOINT = '/.ix-apps'
CONFIG_DATASET = 'app_configs'
APPS_MOUNT_DATASET = 'app_mounts'
CATALOG_DATASET = 'truenas_catalog'
```

### Helper Functions
- `get_docker_dataset()` - Get Docker dataset path
- `get_docker_datasets()` - List all Docker datasets
- `normalize_reference()` - Dataset name normalization

## Best Practices

### 1. Pool Selection
- Use dedicated pool for Docker if possible
- Ensure adequate space for containers
- Consider SSD pools for performance

### 2. Network Configuration
- Plan address pools to avoid conflicts
- Enable IPv6 if needed
- Configure proxy settings if required

### 3. Backup Strategy
- Regular backups before updates
- Test restore procedures
- Keep catalog backups separate

### 4. State Monitoring
```python
# Monitor state changes
async for event in client.subscribe('docker.state'):
    if event['fields']['state'] == 'FAILED':
        # Handle failure
```

## Troubleshooting

### Common Issues

1. **State stuck in INITIALIZING**
   - Check dataset mount status
   - Verify Docker service logs
   - Ensure pool is imported

2. **Migration failures**
   - Check destination pool space
   - Verify no active containers
   - Review rollback logs

3. **Network conflicts**
   - Check address pool overlaps
   - Verify bridge interfaces
   - Review Docker daemon logs

### Debug Commands
```python
# Check Docker datasets
await client.call('docker.fs_manage.ls_docker_datasets')

# Validate setup
await client.call('docker.state.validate')

# Force state refresh
await client.call('docker.state.refresh')
```

## Error Handling

The plugin implements comprehensive error handling:
- Automatic rollback on migration failure
- State recovery mechanisms
- Detailed error reporting
- Filesystem consistency checks

This ensures Docker remains functional even after unexpected failures.