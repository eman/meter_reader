# Socket API (Port 5002)

## Overview

The Socket API is the primary method for communicating with the Rainforest EAGLE gateway. It provides a TCP socket interface on port **5002** that accepts XML commands and returns XML responses. This interface is ideal for real-time data queries and is supported by the `EagleSocketClient` in this library.

## Connection Details

* **Port**: 5002
* **Protocol**: TCP
* **Authentication**: The gateway's local socket API typically operates without authentication (default), though some configurations may require credentials embedded in the XML command payload.

## Command Structure

Commands are sent as XML fragments with the root element `<LocalCommand>`.

### Generic Request Format

```xml
<LocalCommand>
  <Name>command_name</Name>
  <MacId>0xd8d5b90000000cee</MacId>
  <!-- Optional parameters -->
  <StartTime>0x6F123456</StartTime>
  <EndTime>0x6F123789</EndTime>
  <Frequency>0x384</Frequency>
</LocalCommand>
```

**Common Fields:**
- `Name`: Command name (required)
- `MacId` / `DeviceMacId`: Device MAC address (optional; auto-discovered if omitted)
- `StartTime`, `EndTime`: Time range for historical queries (Unix time in hex)
- `Frequency`: Sample interval in seconds (hex) for historical data

### Generic Response Format

All responses are returned as XML without a wrapping root element:

```xml
<InstantaneousDemand>
  <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
  <MeterMacId>0x1122334455667788</MeterMacId>
  <TimeStamp>0x6F123456</TimeStamp>
  <Demand>2468</Demand>
  <Multiplier>1</Multiplier>
  <Divisor>1000</Divisor>
  <DigitsRight>3</DigitsRight>
  <DigitsLeft>5</DigitsLeft>
  <SuppressLeadingZero>0</SuppressLeadingZero>
</InstantaneousDemand>
```

## Supported Commands

### list_devices

Lists all devices (smart meters) paired with the gateway.

**Request:**
```xml
<LocalCommand>
  <Name>list_devices</Name>
</LocalCommand>
```

**Response:**
```xml
<DeviceList>
  <DeviceInfo>
    <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
    <InstallCode>0x1234567890ABCDEF</InstallCode>
    <LinkKey>0x0011223344556677</LinkKey>
    <FWVersion>1.4.48</FWVersion>
    <HWVersion>2.0</HWVersion>
    <ImageType>0x05</ImageType>
    <Manufacturer>Rainforest Automation</Manufacturer>
    <ModelId>EAGLE-200</ModelId>
    <DateCode>2023-01-15</DateCode>
  </DeviceInfo>
  <!-- Multiple DeviceInfo elements for multiple devices -->
</DeviceList>
```

**Response Fields:**
- `DeviceMacId`: Hardware MAC address (42-bit format)
- `InstallCode`: Secure pairing code
- `LinkKey`: ZigBee encryption key
- `FWVersion`: Firmware version
- `HWVersion`: Hardware version
- `ImageType`: Image/model type code
- `Manufacturer`: Device manufacturer
- `ModelId`: Model identifier
- `DateCode`: Manufacturing date

### get_instantaneous_demand

Returns real-time power demand measurement.

**Request:**
```xml
<LocalCommand>
  <Name>get_instantaneous_demand</Name>
  <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
</LocalCommand>
```

**Response:**
```xml
<InstantaneousDemand>
  <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
  <MeterMacId>0x1122334455667788</MeterMacId>
  <TimeStamp>0x6F123456</TimeStamp>
  <Demand>2468</Demand>
  <Multiplier>1</Multiplier>
  <Divisor>1000</Divisor>
  <DigitsRight>3</DigitsRight>
  <DigitsLeft>5</DigitsLeft>
  <SuppressLeadingZero>0</SuppressLeadingZero>
</InstantaneousDemand>
```

**Response Fields:**
- `Demand`: Raw demand integer (scaled by Multiplier/Divisor)
- `Multiplier` / `Divisor`: Scaling factors for unit conversion
- `DigitsRight` / `DigitsLeft`: Decimal precision information
- `TimeStamp`: Measurement time (seconds since 2000-01-01, hex)

**Calculation:** `Actual Demand (kW) = (Demand × Multiplier) ÷ Divisor`

### get_device_data

Returns a comprehensive snapshot including demand, summation, and network information.

**Request:**
```xml
<LocalCommand>
  <Name>get_device_data</Name>
  <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
</LocalCommand>
```

**Response:**
```xml
<DeviceData>
  <InstantaneousDemand>
    <!-- Same structure as get_instantaneous_demand -->
  </InstantaneousDemand>
  <CurrentSummation>
    <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
    <MeterMacId>0x1122334455667788</MeterMacId>
    <TimeStamp>0x6F123456</TimeStamp>
    <SummationDelivered>12345678</SummationDelivered>
    <SummationReceived>0</SummationReceived>
    <Multiplier>1</Multiplier>
    <Divisor>1000</Divisor>
    <DigitsRight>3</DigitsRight>
    <DigitsLeft>8</DigitsLeft>
    <SuppressLeadingZero>0</SuppressLeadingZero>
  </CurrentSummation>
  <NetworkInfo>
    <!-- See get_network_info -->
  </NetworkInfo>
</DeviceData>
```

### get_network_info

Returns ZigBee network status and signal strength.

**Request:**
```xml
<LocalCommand>
  <Name>get_network_info</Name>
  <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
</LocalCommand>
```

**Response:**
```xml
<NetworkInfo>
  <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
  <CoordMacId>0x000d6f000a9069e7</CoordMacId>
  <Status>Connected</Status>
  <Description>Device is connected</Description>
  <ExtPanId>0x000d6ffffeFEXXXX</ExtPanId>
  <Channel>15</Channel>
  <ShortAddr>0x1234</ShortAddr>
  <LinkStrength>87</LinkStrength>
</NetworkInfo>
```

**Response Fields:**
- `Status`: Connection status (`"Connected"`, `"Joining"`, `"Unavailable"`)
- `Channel`: ZigBee channel in use (11-26, typically 11-15)
- `LinkStrength`: Signal strength percentage (0-100)
- `ExtPanId`: Extended PAN ID for the ZigBee mesh

### get_history_data

Returns historical energy consumption data in time intervals.

**Request:**
```xml
<LocalCommand>
  <Name>get_history_data</Name>
  <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
  <StartTime>0x6F123456</StartTime>
  <EndTime>0x6F123789</EndTime>
  <Frequency>0x384</Frequency>
</LocalCommand>
```

**Parameters:**
- `StartTime`: Query start time (seconds since 2000-01-01, hex format)
- `EndTime`: Query end time (seconds since 2000-01-01, hex format)
- `Frequency`: Sample interval in seconds (hex); common values:
  - `0x384` = 900 seconds = 15 minutes
  - `0x708` = 1800 seconds = 30 minutes
  - `0xE10` = 3600 seconds = 1 hour

**Response:**
```xml
<HistoryData>
  <CurrentSummation>
    <DeviceMacId>0xd8d5b90000000cee</DeviceMacId>
    <MeterMacId>0x1122334455667788</MeterMacId>
    <TimeStamp>0x6F123456</TimeStamp>
    <SummationDelivered>12345600</SummationDelivered>
    <SummationReceived>0</SummationReceived>
    <Multiplier>1</Multiplier>
    <Divisor>1000</Divisor>
    <DigitsRight>3</DigitsRight>
    <DigitsLeft>8</DigitsLeft>
    <SuppressLeadingZero>0</SuppressLeadingZero>
  </CurrentSummation>
  <!-- Multiple CurrentSummation elements for each interval -->
  <CurrentSummation>
    <TimeStamp>0x6F123789</TimeStamp>
    <SummationDelivered>12346000</SummationDelivered>
    <!-- ... -->
  </CurrentSummation>
</HistoryData>
```

**Note:** This command can return large responses if querying long time periods. The response may be truncated by the gateway if the dataset exceeds internal buffer limits.

## Unsupported Commands

The following commands are documented in official EAGLE documentation but are **rejected** by the device during testing:

- `get_price`: Price information not exposed via socket API
- `get_message`: Message queue not accessible via socket API
- `get_current_summation`: Use `get_device_data` or `get_history_data` instead
- `set_price`: Use HTTP API for configuration changes (if supported)

## Python Client Usage

The `EagleSocketClient` handles all XML generation and response parsing automatically. See the [Clients documentation](../api/clients.md#socket-client) for examples.

## Real-Time Monitoring and Polling

The primary approach for real-time monitoring is **polling-based** queries, where you initiate periodic requests to the gateway. The Socket API is designed to be efficient for this use case.

### Polling Strategy

**Optimal polling intervals depend on your use case:**

- **Demand monitoring**: 10-30 seconds (balance between responsiveness and traffic)
- **Energy summation**: 5-60 minutes (changes slowly, no need for frequent updates)
- **Network status**: 30-300 seconds (diagnostic purposes)
- **Historical data**: Query on-demand (no continuous polling needed)

### Example: Real-Time Demand Monitor

```python
import time
from meter_reader import EagleSocketClient

client = EagleSocketClient("192.168.1.100")

print("Starting real-time monitoring (Ctrl+C to stop)...")
while True:
    try:
        demand = client.get_instantaneous_demand()
        timestamp = demand.timestamp.strftime("%H:%M:%S")
        print(f"[{timestamp}] {demand.panic_demand:.3f} kW")
        time.sleep(10)  # Query every 10 seconds
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
```

### Example: Alert on High Demand

```python
import time
from meter_reader import EagleSocketClient

client = EagleSocketClient("192.168.1.100")
THRESHOLD_KW = 5.0
last_alert_time = 0
ALERT_COOLDOWN = 300  # Don't send alerts more than once per 5 minutes

while True:
    try:
        demand = client.get_instantaneous_demand()
        current_time = time.time()
        
        if demand.panic_demand > THRESHOLD_KW:
            if current_time - last_alert_time > ALERT_COOLDOWN:
                print(f"ALERT: Demand {demand.panic_demand:.2f} kW exceeds threshold!")
                # Send email, webhook, or notification here
                last_alert_time = current_time
        
        time.sleep(10)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
```

### Performance Considerations

**Socket connection efficiency:**

- The Socket API is optimized for sequential queries on a single connection
- Opening a new socket for each query adds 50-200ms latency
- Reuse client instances: `client = EagleSocketClient(...)` once, then call methods repeatedly
- The `EagleSocketClient` automatically manages socket lifecycle for you

**Monitoring scale:**

- A single client can poll the gateway 5-10 times per second (practical limit ~100ms per query)
- For multiple independent monitors, use separate client instances
- Gateway responsiveness is not affected by polling frequency (local network only)

**Network impact:**

- 1 query every 10 seconds = ~360 queries/hour ≈ 500 bytes/hour network traffic
- Polling is extremely lightweight on local networks
- Socket protocol is more efficient than HTTP for frequent queries

### Event Notifications and Callbacks

The EAGLE Gateway may support event notification and callback configuration, though complete documentation is beyond the scope of this library. The gateway may support:

- Event/alert registration
- Callback URLs for remote notifications
- Integration with external services

However, the meter_reader library provides no built-in support for these features. To use them:

1. Refer to the official EAGLE REST API documentation
2. Configure through the gateway's web interface (`/cgi-bin/post_manager` endpoint)
3. Or implement application-level monitoring via polling (as shown above)

This library focuses on efficient, polling-based meter data retrieval.
