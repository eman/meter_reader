# Clients API

The `meter_reader` library provides two client implementations for the EAGLE Gateway, each suited to different deployment scenarios and authentication requirements.

## Overview

Both clients inherit from the abstract `EagleClient` base class, which defines the common interface for interacting with the gateway. Choose based on your gateway's network configuration and authentication setup:

* **Socket API**: Fast, low-overhead XML-based communication (Port 5002)
* **HTTP API**: Standard HTTP with JSON responses and authentication support (Port 80)

## Base Client Interface

::: meter_reader.clients.base.EagleClient
    handler: python
    options:
      members:
        - get_instantaneous_demand
        - get_usage_data
        - list_devices
        - get_network_info
        - get_current_summation

All implementations must provide these methods, ensuring consistent behavior across protocols.

## Socket Client

The `EagleSocketClient` communicates via the raw TCP socket API on port 5002. This is the fastest and lowest-latency option, making it ideal for real-time monitoring and historical data queries.

### Usage Example

```python
from meter_reader import EagleSocketClient

# Connect to the gateway
client = EagleSocketClient("192.168.1.100")

# Get real-time demand
demand = client.get_instantaneous_demand()
print(f"Current Demand: {demand.panic_demand:.2f} kW")

# Get total consumption
summation = client.get_current_summation()
print(f"Delivered: {summation.delivered_kwh:.2f} kWh")

# List connected devices
devices = client.list_devices()
for device in devices.device_info:
    print(f"Device: {device.device_mac_id}")

# Get network status
network = client.get_network_info()
print(f"Link Strength: {network.link_strength}%")

# Get historical data (last hour, 15-minute intervals)
from datetime import datetime, timedelta, timezone
history = client.get_history_data(
    start_time=datetime.now(timezone.utc) - timedelta(hours=1),
    frequency=0x384  # 15 minutes in seconds (900)
)
for entry in history:
    print(f"{entry.timestamp}: {entry.delivered_kwh:.2f} kWh")
```

::: meter_reader.clients.socket.EagleSocketClient
    handler: python
    options:
      members:
        - __init__
        - list_devices
        - get_instantaneous_demand
        - get_current_summation
        - get_usage_data
        - get_network_info
        - get_history_data

## HTTP Client

The `EagleHttpClient` communicates via HTTP POST requests to the `/cgi-bin/cgi_manager` endpoint on port 80. Responses are returned as JSON. This client supports username/password authentication and is useful for deployments where HTTP is preferred over raw sockets.

### Usage Example

```python
from meter_reader import EagleHttpClient

# Connect with credentials
client = EagleHttpClient(
    "192.168.1.100",
    username="admin",
    password="password"
)

# Get usage data (combines demand and summation)
usage = client.get_usage_data()
print(f"Demand: {usage.demand} {usage.demand_units}")
print(f"Delivered: {usage.summation_delivered} {usage.summation_units}")
print(f"Meter Status: {usage.meter_status}")

# List connected devices
devices = client.list_devices()
for device in devices.device_info:
    print(f"Device MAC: {device.device_mac_id}")
    print(f"Model ID: {device.model_id}")

# Get demand (synthesized from usage data)
demand = client.get_instantaneous_demand()
print(f"Demand: {demand.demand:.2f}")

# Get summation (synthesized from usage data)
summation = client.get_current_summation()
print(f"Total Delivered: {summation.delivered_kwh:.2f} kWh")
```

::: meter_reader.clients.http.EagleHttpClient
    handler: python
    options:
      members:
        - __init__
        - list_devices
        - get_usage_data
        - get_instantaneous_demand
        - get_current_summation

## Choosing Between Socket and HTTP

| Feature | Socket | HTTP |
|---------|--------|------|
| Protocol | TCP on port 5002 | HTTP POST on port 80 |
| Data Format | XML | JSON |
| Authentication | Optional, in XML payload | HTTP Basic Auth |
| Speed | Fastest | Slightly higher latency |
| Firewall Friendly | May require port 5002 | Standard HTTP port |
| Real-time Monitoring | Excellent | Good |
| Historical Queries | Native support | Limited |

### Recommendation

* Use **Socket API** if you need the lowest latency, historical data queries, or the device has port 5002 open
* Use **HTTP API** if you need standard HTTP authentication, prefer JSON, or must operate within strict firewall rules
