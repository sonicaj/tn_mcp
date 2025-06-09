# Virtualization (Virt) Plugin

## Overview
The virt plugin provides virtualization capabilities in TrueNAS through Incus (formerly LXD), supporting both containers (LXC) and virtual machines (VMs). It offers comprehensive management of virtual instances with deep integration into TrueNAS storage and networking.

## Architecture

### Core Services

#### 1. **VirtGlobalService** (`global.py`)
Manages the overall virtualization environment setup and configuration.

**Key Responsibilities:**
- Configure which ZFS pool(s) to use with Incus
- Bootstrap and teardown Incus environment
- Manage network bridge configuration
- Handle service lifecycle and recovery

**Key Methods:**
- `config()` - Get current virt configuration
- `update()` - Update pool and network settings
- `ensure_virt_set()` - Ensure virt is properly configured
- `remove_pool()` - Remove a pool from virt configuration
- `reset()` - Complete reset of virt environment

**Configuration Flow:**
```python
# Set up virtualization
await client.call('virt.global.update', {
    'pool': 'tank',
    'bridge': 'incusbr0',
    'v4_network': '10.0.10.1/24'
})
```

#### 2. **VirtInstanceService** (`instance.py`)
Full CRUD operations for managing containers and VMs.

**Key Methods:**
- `query()` - List instances with filters
- `create()` - Create new container/VM
- `update()` - Modify instance configuration
- `delete()` - Remove instance
- `start/stop/restart()` - Lifecycle management
- `remote_images()` - Available images from remotes

**Instance Types:**
- **CONTAINER**: LXC containers (lightweight, shared kernel)
- **VM**: Full virtual machines (isolated, own kernel)

**Creation Example:**
```python
# Create a container
await client.call('virt.instance.create', {
    'name': 'mycontainer',
    'type': 'CONTAINER',
    'source_type': 'REMOTE_IMAGE',
    'image': {'os': 'ubuntu', 'release': '22.04'},
    'devices': [
        {
            'name': 'root',
            'type': 'DISK',
            'source': {'type': 'VOLUME', 'volume_name': 'rootfs'}
        }
    ]
})
```

#### 3. **VirtInstanceDeviceService** (`instance_device.py`)
Manages devices attached to instances.

**Device Types:**
- **DISK**: Storage devices (ZVOLs, volumes, paths)
- **NIC**: Network interfaces
- **USB**: USB device passthrough
- **GPU**: GPU passthrough (physical mode)
- **PCI**: PCI device passthrough
- **CD-ROM**: ISO mounting
- **TPM**: Trusted Platform Module
- **PROXY**: Port forwarding

**Device Management:**
```python
# Add a disk to instance
await client.call('virt.instance.device.add', {
    'instance_name': 'myvm',
    'device': {
        'name': 'storage',
        'type': 'DISK',
        'source': {'type': 'ZVOL', 'zvol': 'tank/vms/myvm-disk'}
    }
})
```

### Supporting Services

#### 4. **VirtVolumeService** (`volume.py`)
Manages storage volumes for instances.

**Features:**
- Create volumes from scratch
- Import ISOs for VM installation
- Import ZVOLs as volumes
- Size management and expansion

#### 5. **VirtDeviceService** (`device.py`)
Provides available device choices for assignment.

**Methods:**
- `usb_choices()` - Available USB devices
- `gpu_pci_ids_choices()` - Available GPUs
- `disk_choices()` - Available disk paths
- `nic_choices()` - Network interfaces

#### 6. **VirtDiskService** (`disk.py`)
Import/export disk images.

**Supported Formats:**
- QCOW2, QED, RAW, VDI, VPC, VMDK

**Usage:**
```python
# Import disk image to ZVOL
await client.call('virt.disk.import_disk_image', {
    'source_type': 'FILE',
    'source': '/mnt/pool/images/vm.qcow2',
    'destination': 'tank/vms/imported-disk'
})
```

## Key Concepts

### Storage Architecture
- **Storage Pools**: ZFS pools used by Incus
- **Volumes**: Managed storage for instance disks
- **ZVOLs**: Direct ZFS volumes for VMs
- **Paths**: Direct filesystem access for containers

### Network Architecture
- **Bridge Mode**: Default incusbr0 bridge
- **MACVLAN**: Direct connection to physical network
- **Custom Bridges**: Integration with existing bridges

### Instance Configuration

#### Container-Specific:
```python
{
    'type': 'CONTAINER',
    'privileged': False,  # Security mode
    'raw': {             # Raw LXC config
        'lxc.apparmor.profile': 'unconfined'
    }
}
```

#### VM-Specific:
```python
{
    'type': 'VM',
    'cpu': '4',
    'memory': '8192',
    'autostart': True,
    'vnc_enabled': True,
    'vnc_port': 5900,
    'vnc_password': 'secret',
    'secure_boot': False
}
```

## Utilities (`utils.py`)

### Key Functions:
- `get_incus_client()` - Incus API client
- `validate_instance_source()` - Source validation
- `incus_name_is_valid()` - Name validation
- `convert_zfs_pool_to_incus_pool()` - Pool name conversion
- `get_instance_qemu_args()` - QEMU command generation

### Constants:
```python
INCUS_IMAGES_SERVER = 'https://images.linuxcontainers.org'
VNC_BASE_PORT = 5900
CONTAINER_DEVICE_TYPES = {'DISK', 'NIC', 'PROXY', 'USB', 'GPU'}
VM_DEVICE_TYPES = {'DISK', 'NIC', 'CD-ROM', 'USB', 'TPM', 'PCI', 'GPU'}
```

## Device Configuration Examples

### Disk Device
```python
{
    'name': 'root',
    'type': 'DISK',
    'source': {
        'type': 'VOLUME',  # or 'ZVOL', 'PATH'
        'volume_name': 'rootfs'
    },
    'destination': '/dev/sda',  # VM only
    'boot_priority': 1          # VM boot order
}
```

### Network Device
```python
{
    'name': 'eth0',
    'type': 'NIC',
    'network': 'BRIDGED',  # or 'MACVLAN'
    'parent': 'incusbr0'   # Bridge/interface name
}
```

### USB Passthrough
```python
{
    'name': 'usb1',
    'type': 'USB',
    'bus': '001',
    'dev': '003',
    'vendor_id': '1234',
    'product_id': '5678'
}
```

## WebSocket Events (`websocket.py`)

The plugin provides real-time events via WebSocket:
- Instance state changes
- Operation progress
- Error notifications

## Recovery Mechanisms (`recover.py`)

Handles instance recovery scenarios:
- Broken device configurations
- Missing storage paths
- Invalid network configurations

## Best Practices

### 1. Storage Management
- Use volumes for root disks
- Use ZVOLs for additional VM storage
- Keep ISOs in a dedicated dataset

### 2. Network Configuration
- Use default bridge for simple setups
- Use MACVLAN for direct network access
- Configure static IPs via cloud-init

### 3. Resource Allocation
- Set appropriate CPU/memory limits
- Use autostart for critical instances
- Monitor resource usage via stats

### 4. Security
- Use unprivileged containers when possible
- Enable secure boot for VMs
- Limit device passthrough access

## Troubleshooting

### Common Issues:
1. **Pool not configured**: Ensure virt.global is set up
2. **Bridge missing**: Check network configuration
3. **Device conflicts**: Verify device availability
4. **License issues**: Check virt licensing

### Debug Commands:
```python
# Check virt status
await client.call('virt.global.config')

# List all instances
await client.call('virt.instance.query')

# Get instance logs
await client.call('virt.instance.logs', 'instance_name')
```

## Integration Points

- **Reporting**: Real-time metrics via `virt.stats`
- **Filesystem**: Dataset dependencies tracked
- **Network**: Port management and validation
- **Services**: Incus service lifecycle
- **ZFS**: Deep storage integration