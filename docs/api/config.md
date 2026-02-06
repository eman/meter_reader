# Configuration API

The `EagleConfigClient` provides access to system-level gateway configuration and status information through the `/cgi-bin/post_manager` HTTP endpoint. This is distinct from meter data retrieval and covers gateway administration.

## Overview

The configuration client enables:
- **Network services**: Enable/disable mDNS for local discovery
- **Remote management**: Configure Rainforest Remote access
- **Cloud integration**: Check cloud service connectivity
- **Device information**: Query firmware, hardware, and MAC address
- **System status**: Check time synchronization, SSH access, and more

All configuration operations require HTTP Basic Authentication.

## Basic Usage

```python
from meter_reader import EagleConfigClient

# Create configuration client
config = EagleConfigClient(
    "192.168.1.100",
    username="admin",
    password="password"
)

# Check mDNS status
mdns = config.get_mdns_status()
print(f"mDNS Enabled: {mdns}")

# Get device configuration
device = config.get_device_config()
print(f"Firmware: {device.get('FirmwareVersion')}")

# Check cloud connectivity
cloud = config.get_cloud_status()
print(f"Cloud Connected: {cloud}")

# Get remote management status
remote = config.get_remote_management_status()
print(f"Remote Enabled: {remote}")
```

## Configuration Commands

### mDNS (Multicast DNS)

mDNS allows the gateway to be discovered on the local network using a hostname (e.g., `eagle-000cee.local`) instead of requiring its IP address.

#### get_mdns_status()

Query mDNS configuration and status.

```python
mdns = config.get_mdns_status()
print(mdns)
```

**Response Example:**
```json
{
  "mDnsStatus": {
    "Enabled": "Y",
    "Hostname": "eagle-000cee",
    "Status": "Active"
  }
}
```

#### set_mdns(enabled: bool)

Enable or disable mDNS service.

```python
# Enable mDNS
response = config.set_mdns(enabled=True)

# Disable mDNS
response = config.set_mdns(enabled=False)
```

### Device Configuration

#### get_device_config()

Get gateway device information and configuration.

```python
config_data = config.get_device_config()
print(f"Firmware: {config_data.get('FirmwareVersion')}")
print(f"Hardware: {config_data.get('HardwareVersion')}")
print(f"MAC Address: {config_data.get('MacAddress')}")
```

**Response Example:**
```json
{
  "FirmwareVersion": "1.4.48",
  "HardwareVersion": "2.0",
  "MacAddress": "00:0D:6F:00:0A:90:69:E7",
  "ModelID": "EAGLE-200",
  "ManufacturerID": "Rainforest Automation",
  "UpdateStatus": "Current",
  "UpdateAvailable": "N"
}
```

### Cloud Service Integration

The EAGLE Gateway can optionally integrate with cloud services for remote monitoring and data aggregation.

#### get_cloud_status()

Check cloud service connectivity and configuration.

```python
cloud = config.get_cloud_status()
if cloud.get('CloudStatus', {}).get('Connected') == 'Y':
    print("Cloud connection active")
```

**Response Example:**
```json
{
  "CloudStatus": {
    "Connected": "Y",
    "Provider": "Rainforest",
    "LastUpdate": "2024-02-06T20:08:43Z",
    "AccountStatus": "Active"
  }
}
```

**Cloud Integration Options:**
- **Rainforest Cloud**: Official cloud service from manufacturer
- **Custom webhooks/callbacks**: May be configurable for external services
- See gateway web interface for cloud configuration details

### Remote Management

Remote Management (Rainforest Remote) allows secure off-site access to the gateway for monitoring and configuration through Rainforest's cloud service.

#### get_remote_management_status()

Check remote management service status.

```python
remote = config.get_remote_management_status()
print(f"Remote enabled: {remote.get('RemoteEnabled')}")
print(f"Remote status: {remote.get('RemoteStatus')}")
```

**Response Example:**
```json
{
  "RemoteEnabled": "Y",
  "RemoteStatus": "Connected",
  "LastConnection": "2024-02-06T20:05:00Z",
  "Provider": "Rainforest"
}
```

#### set_remote_management(enabled: bool)

Enable or disable remote management service.

```python
# Enable remote management
response = config.set_remote_management(enabled=True)

# Disable remote management  
response = config.set_remote_management(enabled=False)
```

### System Information

#### get_time_status()

Get gateway time and NTP (Network Time Protocol) synchronization status.

```python
time_info = config.get_time_status()
print(f"Current time: {time_info.get('CurrentTime')}")
print(f"NTP status: {time_info.get('NtpStatus')}")
print(f"Time zone: {time_info.get('TimeZone')}")
```

**Response Example:**
```json
{
  "CurrentTime": "2024-02-06T20:08:43Z",
  "NtpStatus": "Synchronized",
  "NtpServer": "pool.ntp.org",
  "TimeZone": "UTC",
  "DaylightSavings": "N"
}
```

#### get_network_info()

Get gateway network configuration.

```python
network = config.get_network_info()
print(f"IP Address: {network.get('IPAddress')}")
print(f"Netmask: {network.get('Netmask')}")
print(f"Gateway: {network.get('Gateway')}")
print(f"DHCP: {network.get('DHCP')}")
```

**Response Example:**
```json
{
  "IPAddress": "192.168.1.100",
  "Netmask": "255.255.255.0",
  "Gateway": "192.168.1.1",
  "DNS1": "192.168.1.1",
  "DNS2": "8.8.8.8",
  "DHCP": "Y",
  "Hostname": "eagle-000cee"
}
```

#### get_ssh_status()

Get SSH (Secure Shell) access status (if available).

```python
ssh = config.get_ssh_status()
print(f"SSH enabled: {ssh}")
```

## Advanced Usage

### Generic Command Execution

For commands not explicitly supported by this client, use `run_command()`:

```python
# Execute any post_manager command
response = config.run_command('get_mdns_status')

# With parameters
response = config.run_command('some_command', Param1='value1', Param2='value2')
```

### Integration Example: Configuration Check

```python
from meter_reader import EagleConfigClient

def check_gateway_health(address: str, username: str, password: str) -> dict:
    """Perform a comprehensive gateway health check."""
    config = EagleConfigClient(address, username, password)
    
    try:
        # Gather system information
        device = config.get_device_config()
        network = config.get_network_info()
        time_info = config.get_time_status()
        cloud = config.get_cloud_status()
        remote = config.get_remote_management_status()
        
        return {
            "device": {
                "firmware": device.get('FirmwareVersion'),
                "hardware": device.get('HardwareVersion'),
                "update_available": device.get('UpdateAvailable') == 'Y',
            },
            "network": {
                "ip_address": network.get('IPAddress'),
                "dhcp_enabled": network.get('DHCP') == 'Y',
            },
            "system": {
                "time_synchronized": time_info.get('NtpStatus') == 'Synchronized',
            },
            "cloud": {
                "connected": cloud.get('CloudStatus', {}).get('Connected') == 'Y',
            },
            "remote": {
                "enabled": remote.get('RemoteEnabled') == 'Y',
                "connected": remote.get('RemoteStatus') == 'Connected',
            },
        }
    except Exception as e:
        return {"error": str(e)}

# Usage
health = check_gateway_health("192.168.1.100", "admin", "password")
print(health)
```

## API Reference

::: meter_reader.clients.config.EagleConfigClient
    handler: python
    options:
      members:
        - __init__
        - get_mdns_status
        - set_mdns
        - get_device_config
        - get_cloud_status
        - get_remote_management_status
        - set_remote_management
        - get_ssh_status
        - get_time_status
        - get_network_info
        - run_command

## Configuration Discovery

The gateway's configuration interface is available via HTTP at:
- **Default**: `http://192.168.1.100` (replace with your gateway IP)
- **Via mDNS**: `http://eagle-XXXXXX.local` (if mDNS is enabled)

Use the web interface to:
- View additional configuration details
- Configure event callbacks and notifications
- Manage cloud service accounts
- Update firmware
- Reset gateway to factory defaults
- Configure advanced settings

## Notes

- Configuration changes may require gateway restart
- Some configuration operations may be restricted based on gateway firmware version
- The gateway may support additional post_manager commands beyond those documented here
- Refer to the official EAGLE REST API documentation for complete command reference
