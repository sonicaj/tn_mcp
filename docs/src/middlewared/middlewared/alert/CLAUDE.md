# Alert Subsystem

## Overview
The alert subsystem monitors TrueNAS system health and notifies administrators about issues. It consists of alert sources that detect problems and alert services that send notifications.

## Directory Structure

- **`base.py`** - Base classes for alerts
- **`schedule.py`** - Alert scheduling and frequency control
- **`source/`** - Alert detection modules
- **`service/`** - Notification service implementations

## Core Concepts

### Alert Levels
```python
class AlertLevel(enum.Enum):
    INFO = 10
    NOTICE = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    ALERT = 60
    EMERGENCY = 70
```

### Alert Classes
Defined in `base.py`:

1. **Alert** - Base alert class
   - `level` - Severity level
   - `title` - Short description
   - `text` - Detailed message
   - `datetime` - When alert was raised
   - `dismissed` - Whether user dismissed it

2. **AlertSource** - Base class for alert detectors
   - `schedule` - How often to check
   - `run()` - Check for issues and return alerts

3. **AlertService** - Base class for notification services
   - `send()` - Send alert via service
   - `config_schema` - Service configuration

## Alert Sources (`/source/`)

### Common Alert Sources

#### System Health
- **`cores.py`** - System core dumps
- **`memory_errors.py`** - ECC memory errors
- **`disk_temp.py`** - Disk temperature warnings
- **`smart.py`** - S.M.A.R.T. disk errors
- **`sensors.py`** - Hardware sensor alerts

#### Storage
- **`pools.py`** - Pool health and status
- **`volume_status.py`** - Volume degradation
- **`zpool_capacity.py`** - Pool capacity warnings
- **`quota.py`** - Dataset quota alerts
- **`scrub_paused.py`** - Scrub operation issues

#### Services
- **`active_directory.py`** - AD connection issues
- **`certificates.py`** - Certificate expiration
- **`ntp.py`** - Time sync problems
- **`ssh_login_failures.py`** - Security alerts
- **`update.py`** - System update availability

### Creating Alert Sources

```python
from middlewared.alert.base import AlertSource, Alert, AlertLevel
from middlewared.alert.schedule import CrontabSchedule

class MyAlertSource(AlertSource):
    # Run every hour
    schedule = CrontabSchedule(hour="*")
    
    # Run only on HA systems
    run_on_backup_node = False
    
    async def check(self):
        alerts = []
        
        # Check for issues
        issues = await self.middleware.call('my.service.check_issues')
        
        for issue in issues:
            alerts.append(Alert(
                title=f"Issue detected: {issue['name']}",
                text=f"Details: {issue['details']}",
                level=AlertLevel.WARNING,
                # Optional fields
                key=issue['id'],  # For deduplication
                _metadata={'issue_id': issue['id']}
            ))
        
        return alerts
```

### Alert Source Patterns

#### One-Shot Alerts
```python
class CertificateAlert(AlertSource):
    async def check(self):
        alerts = []
        for cert in await self.middleware.call('certificate.query'):
            if cert['cert_alerts']:
                alerts.append(Alert(
                    title=f"Certificate '{cert['name']}' expiring",
                    level=AlertLevel.WARNING,
                    key=cert['id']  # Prevents duplicates
                ))
        return alerts
```

#### Conditional Alerts
```python
class ServiceAlert(AlertSource):
    async def check(self):
        if not await self.middleware.call('service.started', 'ssh'):
            return []  # No alerts if service not running
            
        # Check service-specific issues
        return alerts
```

## Alert Services (`/service/`)

### Available Services
- **`mail.py`** - Email notifications
- **`slack.py`** - Slack webhooks
- **`mattermost.py`** - Mattermost webhooks
- **`pagerduty.py`** - PagerDuty integration
- **`victorops.py`** - VictorOps integration
- **`opsgenie.py`** - Opsgenie integration
- **`snmp_trap.py`** - SNMP traps
- **`influxdb_.py`** - InfluxDB metrics
- **`telegram.py`** - Telegram messages
- **`aws_sns.py`** - AWS SNS

### Creating Alert Services

```python
from middlewared.alert.service.base import ProThreadedAlertService

class MyAlertService(ProThreadedAlertService):
    title = "My Alert Service"
    
    schema = Dict(
        'myalert_attributes',
        Str('api_key', required=True),
        Str('endpoint', default='https://api.example.com')
    )
    
    def send_sync(self, alerts, config):
        # This runs in a thread pool
        import requests
        
        for alert in alerts:
            response = requests.post(
                config['endpoint'],
                headers={'Authorization': f"Bearer {config['api_key']}"},
                json={
                    'title': alert.formatted_title,
                    'message': alert.formatted_text,
                    'level': alert.level.name,
                    'timestamp': alert.datetime.isoformat()
                }
            )
            response.raise_for_status()
```

## Alert Configuration

### Database Schema
Alerts are configured in the database:
- Alert services: `system_alertservice` table
- Alert settings: Per-source configuration

### API Methods
In `alert.py` plugin:
```python
# List current alerts
alerts = await client.call('alert.list')

# Dismiss an alert
await client.call('alert.dismiss', alert_uuid)

# Test alert service
await client.call('alertservice.test', {
    'type': 'mail',
    'attributes': {...}
})
```

## Alert Scheduling

### Schedule Types

```python
# Run every 5 minutes
IntervalSchedule(minutes=5)

# Run hourly at :30
CrontabSchedule(minute=30)

# Run daily at 2 AM
CrontabSchedule(hour=2, minute=0)

# Custom schedule
CustomSchedule(lambda now: now.hour == 0)
```

### Performance Considerations
- Alerts run in parallel
- Heavy checks should be async
- Cache results when appropriate
- Use appropriate schedules

## Best Practices

### 1. Alert Design
- Clear, actionable titles
- Detailed text with context
- Appropriate severity levels
- Include resolution steps

### 2. Deduplication
- Use `key` field for unique alerts
- Prevents spam from repeated issues
- Alerts with same key update existing

### 3. Performance
```python
class EfficientAlert(AlertSource):
    # Run less frequently for expensive checks
    schedule = CrontabSchedule(hour="*/6")
    
    async def check(self):
        # Cache expensive operations
        if not hasattr(self, '_cache_time'):
            self._cache_time = 0
            
        now = time.time()
        if now - self._cache_time > 3600:
            self._cache = await expensive_operation()
            self._cache_time = now
```

### 4. Testing
```python
# Test alert source directly
source = MyAlertSource(middleware)
alerts = await source.check()

# Test via API
await client.call('alert.oneshot_create', 'MyAlert', {
    'title': 'Test Alert',
    'level': 'WARNING'
})
```

## Alert Lifecycle

1. **Detection**: Alert sources run on schedule
2. **Creation**: Alerts created with level, text
3. **Deduplication**: Same key updates existing
4. **Notification**: Services send alerts
5. **Display**: UI shows active alerts
6. **Dismissal**: User acknowledges alert
7. **Re-raise**: Alert can reappear if issue persists

## Common Patterns

### Hardware Monitoring
```python
if temperature > threshold:
    return [Alert(
        f"Disk {disk} temperature {temperature}°C exceeds {threshold}°C",
        level=AlertLevel.WARNING
    )]
```

### Service Health
```python
if not service_healthy:
    return [Alert(
        f"Service {name} is not responding",
        level=AlertLevel.ERROR,
        _metadata={'service': name}
    )]
```

### Configuration Issues
```python
if misconfigured:
    return [Alert(
        "Configuration issue detected",
        "Please check: " + details,
        level=AlertLevel.NOTICE
    )]
```