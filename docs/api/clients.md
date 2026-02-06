# Clients API

The `meter_reader` library provides three client implementations for the EAGLE Gateway, each suited to different use cases:

## Overview

* **Socket API Client**: Fast, low-overhead XML-based communication for meter data (Port 5002)
* **HTTP API Client**: Standard HTTP with JSON responses for meter data (Port 80)
* **Configuration Client**: System configuration and gateway administration (Port 80, `/cgi-bin/post_manager`)

Choose based on your use case:
- **Meter data** (demand, summation, history): Use Socket or HTTP client
- **Gateway configuration** (mDNS, remote management, cloud status): Use Configuration client

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

### Basic Usage

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

### Real-Time Monitoring

The Socket API is optimized for real-time monitoring via polling. Here's an example that continuously monitors power demand:

```python
import time
from datetime import datetime
from meter_reader import EagleSocketClient

client = EagleSocketClient("192.168.1.100")

# Monitor demand every 10 seconds
interval = 10
max_duration = 3600  # Monitor for 1 hour

start_time = time.time()
while time.time() - start_time < max_duration:
    try:
        demand = client.get_instantaneous_demand()
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Demand: {demand.panic_demand:.3f} kW")
        
        # Check for high demand (alert condition)
        if demand.panic_demand > 5.0:
            print(f"  ⚠️  ALERT: High demand detected!")
        
        time.sleep(interval)
    except Exception as e:
        print(f"Error reading demand: {e}")
        time.sleep(interval)
```

### Continuous Monitoring with Data Logging

For longer-duration monitoring with data persistence:

```python
import time
import csv
from datetime import datetime
from meter_reader import EagleSocketClient

client = EagleSocketClient("192.168.1.100")

# Log demand data to CSV
with open("demand_log.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Demand (kW)", "Link Strength"])
    
    interval = 30  # Sample every 30 seconds
    samples = 0
    max_samples = 120  # Collect 120 samples (1 hour)
    
    while samples < max_samples:
        try:
            demand = client.get_instantaneous_demand()
            network = client.get_network_info()
            
            timestamp = datetime.now().isoformat()
            writer.writerow([
                timestamp,
                f"{demand.panic_demand:.3f}",
                network.link_strength
            ])
            f.flush()
            
            print(f"Logged sample {samples+1}/{max_samples}")
            samples += 1
            time.sleep(interval)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval)
```

### Periodic Data Collection with Summary

Monitor demand and update hourly summation:

```python
import time
from datetime import datetime, timedelta, timezone
from meter_reader import EagleSocketClient

client = EagleSocketClient("192.168.1.100")

# Track peak demand
peak_demand = 0
peak_time = None

# Monitor with 5-minute interval
interval = 300
duration = 3600  # 1 hour

start_time = time.time()
while time.time() - start_time < duration:
    try:
        demand = client.get_instantaneous_demand()
        
        # Update peak tracking
        if demand.panic_demand > peak_demand:
            peak_demand = demand.panic_demand
            peak_time = demand.timestamp
        
        print(f"Current: {demand.panic_demand:.3f} kW (Peak: {peak_demand:.3f} kW)")
        time.sleep(interval)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(interval)

# Get final summation
print("\n=== Summary ===")
summation = client.get_current_summation()
print(f"Total Delivered: {summation.delivered_kwh:.2f} kWh")
print(f"Peak Demand: {peak_demand:.3f} kW at {peak_time}")
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

## Real-Time Monitoring Architecture

The primary approach for real-time monitoring is **polling (pull) model**, where you initiate periodic queries. The Socket API is optimized for this use case.

### Polling-Based Approach

The Socket API is optimized for polling because:
- **Lower latency**: Direct TCP connection eliminates HTTP overhead
- **Minimal overhead**: Lightweight XML parsing and response handling
- **Historical data**: Native support for querying past data ranges efficiently
- **Connection reuse**: Single socket can handle multiple sequential queries

To implement real-time monitoring:

1. **Periodic polling**: Query the device at regular intervals (5-30 second intervals typical)
2. **External integration**: Use your application logic to detect changes and trigger notifications
3. **Time-series database**: Store readings over time for analysis and alerting

The Socket API is significantly more efficient for frequent polling than HTTP due to reduced per-request overhead.

### Push Notifications and Events

The EAGLE Gateway may support event notification and remote callback configuration, though this library's documentation is limited in this area. The gateway's configuration interface (via `/cgi-bin/post_manager` HTTP endpoint) supports:

- Remote management settings
- Cloud service integration (Rainforest and potentially others)
- Event/notification configuration parameters

However, the meter_reader library currently provides:
- ✅ Efficient polling-based monitoring (recommended approach)
- ❌ No built-in support for event registration or callback setup

For push notification capabilities beyond polling, you may need to:
1. Consult the gateway's official EAGLE_REST_API documentation
2. Configure event callbacks through the gateway's web interface
3. Explore the `/cgi-bin/post_manager` endpoint directly

This library focuses on the core meter data retrieval use cases (polling-based monitoring and historical queries).

## Choosing Between Socket and HTTP

| Feature | Socket | HTTP |
|---------|--------|------|
| Protocol | TCP on port 5002 | HTTP POST on port 80 |
| Data Format | XML | JSON |
| Authentication | Optional, in XML payload | HTTP Basic Auth |
| Speed | Fastest | Slightly higher latency |
| Firewall Friendly | May require port 5002 | Standard HTTP port |
| Real-time Monitoring | Excellent (optimized for polling) | Good |
| Historical Queries | Native support | Limited |
| Continuous Polling | Most efficient | Higher overhead |

### Recommendation

* Use **Socket API** if you need the lowest latency, frequent polling, or historical data queries
* Use **HTTP API** if you need standard HTTP authentication, prefer JSON, or must operate within strict firewall rules
* Use **Cloud API** (external) if you need off-premises access and remote monitoring
