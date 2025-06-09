# Apps Plugin

## Overview
The apps plugin provides a user-friendly interface for deploying Docker-based applications through a catalog system. It abstracts Docker Compose complexity behind a schema-driven configuration interface defined by app developers using `questions.yaml` files.

## Architecture

### Core Concepts

1. **Catalog Apps**: Pre-packaged applications from TrueNAS apps repository
2. **Questions Schema**: YAML-based configuration interface definition
3. **Docker Compose**: Underlying container orchestration
4. **IX Volumes**: ZFS-backed persistent storage for apps

### Directory Structure
```
/mnt/{pool}/ix-apps/app_configs/{app_name}/
├── versions/
│   └── {version}/
│       ├── app.yaml                # Rendered from templates
│       ├── templates/              # Original templates
│       └── values.yaml             # User configuration
├── config.json                     # App metadata
└── metadata.json                   # Runtime metadata
```

## Core Components

### 1. **AppsService** (`crud.py`)
Main CRUD service for app management.

**Key Methods:**
- `query()` - List installed apps with state and workloads
- `create()` - Install app from catalog
- `update()` - Update app configuration
- `delete()` - Remove app and optionally its data
- `get_instance()` - Get single app details

**App Installation Flow:**
```python
# Install app from catalog
await client.call('app.create', {
    'app_name': 'plex',
    'values': {
        'network': {
            'host_network': True,
            'web_port': 32400
        },
        'storage': {
            'config': {
                'type': 'ix_volume',
                'ix_volume_config': {'dataset_name': 'plex_config'}
            }
        }
    },
    'catalog_app': {
        'id': 'plex',
        'train': 'stable'
    }
})
```

### 2. **Schema System** (`schema_validation.py`, `schema_normalization.py`)

#### Questions.yaml Structure:
```yaml
groups:
  - name: Network Configuration
    description: Configure network settings
questions:
  - variable: network.host_network
    label: Use Host Network
    schema:
      type: boolean
      default: false
  - variable: network.web_port
    label: Web Port
    schema:
      type: int
      min: 1
      max: 65535
      default: 8080
      required: true
```

#### Schema Validation:
- Type checking (string, int, boolean, dict, list, etc.)
- Range validation (min/max)
- Required field enforcement
- Custom validators for special types

#### Schema Normalization:
- Certificate references resolution
- GPU configuration processing
- IX volume creation
- ACL permission handling

### 3. **Docker Compose Management** (`compose_utils.py`)

**Key Functions:**
- `compose_action()` - Execute docker compose commands
- Project names prefixed with "ix-" (e.g., `ix-plex`)
- 20-minute timeout for operations
- Automatic orphan removal

**Compose Actions:**
```python
# Start app
await compose_action(app_name, app_version_path, 'up', {
    'force_recreate': True,
    'remove_orphans': True
})

# Stop app
await compose_action(app_name, app_version_path, 'down', {
    'remove_orphans': True,
    'volumes': False  # Preserve data
})
```

### 4. **App Lifecycle** (`app_scale.py`)

**States:**
- `STOPPED` - Not running
- `RUNNING` - All containers running
- `DEPLOYING` - Being deployed
- `STOPPING` - Being stopped
- `CRASHED` - Container failure

**Operations:**
```python
# Start app
await client.call('app.start', 'plex')

# Stop app
await client.call('app.stop', 'plex')

# Redeploy (recreate containers)
await client.call('app.redeploy', 'plex')
```

### 5. **Custom Apps** (`custom_app.py`)

Support for user-provided Docker Compose files:

```python
# Create custom app
await client.call('app.create', {
    'custom_app': True,
    'app_name': 'myapp',
    'custom_compose_config': {
        'version': '3.8',
        'services': {
            'web': {
                'image': 'nginx:latest',
                'ports': ['8080:80']
            }
        }
    }
})
```

## Special Features

### IX Volumes
Special volume type that creates ZFS datasets:
```yaml
storage:
  config:
    type: ix_volume
    ix_volume_config:
      dataset_name: app_config
      properties:
        recordsize: 16K
      acl_enable: true
      acl_entries:
        - id_type: USER
          id: 1000
          access: FULL_CONTROL
```

### GPU Support
```yaml
resources:
  gpus:
    nvidia_gpu_selection:
      - gpu_00000000_02_00_0
```

### Certificate Integration
```yaml
certificates:
  cert_id:
    schema:
      type: int
      $ref:
        - certificate.query
```

### Port Management
- Automatic port collision detection
- Support for host network mode
- TCP/UDP port configuration

## App Operations

### Logs
```python
# Stream container logs
def on_logs(data):
    print(data['log_entry'])

await client.subscribe('app.logs', on_logs, {
    'app_name': 'plex',
    'container_id': 'plex',
    'tail_lines': 100
})
```

### Shell Access
```python
# Execute command in container
await client.call('app.shell', {
    'app_name': 'plex',
    'container_id': 'plex',
    'command': ['/bin/bash']
})
```

### Rollback/Upgrade
```python
# Rollback to previous version
await client.call('app.rollback', {
    'app_name': 'plex',
    'app_version': '1.1.23'
})

# Upgrade to new version
await client.call('app.upgrade', {
    'app_name': 'plex',
    'app_version': '1.1.25'
})
```

## Best Practices

### 1. Schema Design
- Keep questions organized in logical groups
- Provide sensible defaults
- Use show_if conditions for advanced options
- Include helpful descriptions

### 2. Storage Configuration
- Use IX volumes for app data
- Configure appropriate ACLs
- Plan dataset properties (recordsize, compression)

### 3. Network Configuration
- Avoid port conflicts
- Use host network sparingly
- Consider reverse proxy setup

### 4. Resource Management
- Set appropriate CPU/memory limits
- Configure GPU access carefully
- Monitor resource usage

## Troubleshooting

### Common Issues

1. **App stuck in DEPLOYING**
   - Check Docker compose logs
   - Verify image availability
   - Check resource constraints

2. **Port conflicts**
   - Query used ports: `app.used_ports`
   - Change port bindings
   - Use different network mode

3. **Permission issues**
   - Verify ACL configurations
   - Check user/group mappings
   - Review volume permissions

### Debug Commands
```python
# Get app config
config = await client.call('app.config', 'plex')

# Check container status
workloads = await client.call('app.query', [['id', '=', 'plex']], {
    'extra': {'include_app_schema': True}
})

# Force update metadata
await client.call('app.metadata.generate', 'plex')
```

## Integration Points

- **Catalog**: App definitions and versions
- **Docker**: Container runtime
- **Certificates**: TLS certificate management
- **GPU**: Hardware acceleration
- **Network**: Port and interface management
- **Storage**: ZFS dataset creation

The apps plugin provides a powerful abstraction over Docker Compose, making containerized applications accessible to users while maintaining flexibility for advanced configurations.