# Integration Tests Directory

## Overview
This directory contains integration tests for TrueNAS middleware. These tests run against a real TrueNAS system (or VM) and test the full stack including API calls, system changes, and service interactions.

## Test Structure

### Test File Naming Convention
- `test_XXX_description.py` - XXX is a number for ordering
- Lower numbers run first (e.g., `test_001_ssh.py` runs before `test_030_activedirectory.py`)
- Group related tests with similar numbers

### Key Test Categories

#### System Setup (001-050)
- `test_001_ssh.py` - SSH configuration
- `test_005_interface.py` - Network interfaces
- `test_006_pool_and_sysds.py` - Pool and system dataset setup
- `test_011_user.py` - User management

#### Directory Services (030-080)
- `test_030_activedirectory.py` - AD join/leave
- `test_032_ad_kerberos.py` - Kerberos with AD
- `test_275_ldap.py` - LDAP configuration
- `test_278_freeipa.py` - FreeIPA integration

#### Storage Services (260-290)
- `test_260_iscsi.py` - iSCSI targets
- `test_261_iscsi_cmd.py` - iSCSI commands
- `test_262_iscsi_alua.py` - iSCSI ALUA

#### File Sharing (300-450)
- `test_300_nfs.py` - NFS exports
- `test_420_smb.py` - SMB shares
- `test_345_acl_nfs4.py` - NFSv4 ACLs
- `test_427_smb_acl.py` - SMB ACLs

#### System Services (450+)
- `test_440_snmp.py` - SNMP configuration
- `test_475_syslog.py` - Syslog configuration
- `test_530_ups.py` - UPS configuration

## Test Infrastructure

### Key Files
- `conftest.py` - Pytest configuration and fixtures
- `functions.py` - Common test utilities
- `utils.py` - Helper functions
- `runtest.py` - Test runner script

### Protocol Testing (`/protocols/`)
- `ftp_proto.py` - FTP protocol testing
- `iscsi_proto.py` - iSCSI protocol testing
- `nfs_proto.py` - NFS protocol testing
- `smb_proto.py` - SMB protocol testing

### WebSocket Testing (`/assets/websocket/`)
- `server.py` - WebSocket test server
- Protocol-specific WebSocket helpers

## Writing Tests

### Basic Test Structure
```python
import pytest
from functions import GET, POST, PUT, DELETE, SSH_TEST

def test_service_config():
    # GET current config
    config = GET('/service/ssh/config/')
    assert config.status_code == 200
    
    # Update config
    result = PUT('/service/ssh/config/', {
        'enabled': True,
        'port': 22
    })
    assert result.status_code == 200
    
    # Verify change
    new_config = GET('/service/ssh/config/')
    assert new_config.json()['enabled'] is True
```

### Common Patterns

#### Service Testing
```python
def test_service_lifecycle():
    # Configure service
    PUT('/service/name/config/', {...})
    
    # Start service
    POST('/service/start/', {'service': 'servicename'})
    
    # Verify running
    status = GET('/service/status/')
    assert status.json()['servicename'] == 'RUNNING'
    
    # Stop service
    POST('/service/stop/', {'service': 'servicename'})
```

#### CRUD Testing
```python
def test_user_crud():
    # Create
    user = POST('/user/', {
        'username': 'testuser',
        'full_name': 'Test User',
        'password': 'testpass123'
    })
    user_id = user.json()['id']
    
    # Read
    users = GET('/user/')
    assert any(u['username'] == 'testuser' for u in users.json())
    
    # Update
    PUT(f'/user/id/{user_id}/', {'full_name': 'Updated Name'})
    
    # Delete
    DELETE(f'/user/id/{user_id}/')
```

#### WebSocket Testing
```python
from assets.websocket import websocket_call

def test_websocket_pool_create():
    result = websocket_call('pool.create', {
        'name': 'testpool',
        'topology': {...}
    })
    assert result['state'] == 'SUCCESS'
```

### Test Fixtures

Common fixtures in `conftest.py`:
- `request` - Provides test metadata
- `pytestconfig` - Pytest configuration
- Various setup/teardown fixtures

### Environment Variables
Tests use these environment variables:
- `SERVERIP` - TrueNAS server IP
- `SERVERUSER` - API username
- `SERVERPASS` - API password

## Best Practices

### 1. Test Independence
- Each test should be runnable independently
- Clean up resources created during tests
- Don't depend on other test outcomes

### 2. Error Handling
```python
def test_with_cleanup():
    resource_id = None
    try:
        # Create resource
        result = POST('/resource/', {...})
        resource_id = result.json()['id']
        
        # Test operations
        # ...
    finally:
        # Always cleanup
        if resource_id:
            DELETE(f'/resource/id/{resource_id}/')
```

### 3. Assertions
- Use specific assertions with clear messages
- Check status codes before JSON parsing
- Verify side effects (files created, services started)

### 4. Skip Conditions
```python
@pytest.mark.skipif(
    not IS_ENTERPRISE,
    reason="Enterprise feature"
)
def test_enterprise_feature():
    pass
```

### 5. Parametrized Tests
```python
@pytest.mark.parametrize("share_type", ["SMB", "NFS"])
def test_share_creation(share_type):
    # Test logic for both share types
```

## Running Tests

### Individual Tests
```bash
pytest tests/api2/test_420_smb.py::test_smb_create -v
```

### Test Categories
```bash
# All SMB tests
pytest tests/api2/test_42*.py -v

# Skip slow tests
pytest tests/api2/ -m "not slow"
```

### With Coverage
```bash
pytest tests/api2/ --cov=middlewared --cov-report=html
```

## Debugging Tests

### Print Debugging
```python
def test_debug():
    result = GET('/some/endpoint/')
    print(f"Status: {result.status_code}")
    print(f"Response: {result.json()}")
    # Use -s flag to see prints: pytest -s
```

### Interactive Debugging
```python
def test_interactive():
    import pdb; pdb.set_trace()
    # Execution stops here
```

### SSH Debugging
```python
# Use SSH_TEST to run commands
output = SSH_TEST("ls -la /mnt")
print(output)
```

## Common Issues

1. **Test Order Dependencies**: Use proper test ordering numbers
2. **Resource Cleanup**: Always clean up in finally blocks
3. **Timing Issues**: Add appropriate waits for async operations
4. **Permission Issues**: Ensure test user has needed privileges
5. **Network Issues**: Check connectivity to test server