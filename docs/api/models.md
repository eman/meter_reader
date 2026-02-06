# Data Models

The `meter_reader` library uses Pydantic models to ensure type-safe and consistent data structures. All responses from both Socket and HTTP clients are normalized into these models, providing a unified interface regardless of the underlying protocol.

## Model Overview

Pydantic models validate input data and provide computed properties for convenient unit conversions. All timestamp fields are automatically converted to Python `datetime` objects.

## Device Information

### DeviceInfo

Represents a single device (smart meter) connected to the gateway.

::: meter_reader.models.DeviceInfo
    handler: python

**Fields:**
* `device_mac_id`: Hardware MAC address (e.g., `00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE`)
* `install_code`: (Optional) Installation code for secure pairing
* `link_key`: (Optional) ZigBee link key
* `fw_version`: (Optional) Firmware version (e.g., `1.4.48`)
* `hw_version`: (Optional) Hardware version
* `image_type`: (Optional) Image/model type identifier
* `manufacturer`: (Optional) Manufacturer name
* `model_id`: (Optional) Model identifier
* `date_code`: (Optional) Manufacturing date code

### DeviceList

Collection of devices connected to the gateway.

::: meter_reader.models.DeviceList
    handler: python

**Fields:**
* `device_info`: List of `DeviceInfo` objects

**Example Response:**
```json
{
  "device_info": [
    {
      "device_mac_id": "00:11:22:33:44:55:66:77:88:99:AA:BB:CC",
      "fw_version": "1.4.48",
      "hw_version": "2.0",
      "model_id": "EAGLE-200"
    }
  ]
}
```

## Demand Data

### InstantaneousDemand

Real-time power demand measurement.

::: meter_reader.models.InstantaneousDemand
    handler: python

**Fields:**
* `device_mac_id`: MAC address of the reporting device
* `meter_mac_id`: MAC address of the smart meter
* `timestamp`: Time of measurement (UTC)
* `demand`: Raw demand value (integer)
* `multiplier`: Scaling multiplier
* `divisor`: Scaling divisor
* `digits_right`: Decimal places (right of decimal)
* `digits_left`: Significant digits (left of decimal)
* `suppress_leading_zero`: Format flag

**Computed Properties:**
* `panic_demand`: Returns actual demand in kW, calculated as `(demand * multiplier) / divisor`

**Example Response:**
```json
{
  "device_mac_id": "00:11:22:33:44:55:66:77:88:99:AA:BB:CC",
  "meter_mac_id": "00:11:22:33:44:55:66:77",
  "timestamp": "2024-02-06T19:41:00Z",
  "demand": 2468,
  "multiplier": 1,
  "divisor": 1000,
  "digits_right": 3,
  "digits_left": 5,
  "suppress_leading_zero": false
}
```

The `panic_demand` property automatically handles unit conversion: `(2468 * 1) / 1000 = 2.468 kW`

## Summation Data

### CurrentSummation

Cumulative energy consumption totals.

::: meter_reader.models.CurrentSummation
    handler: python

**Fields:**
* `device_mac_id`: MAC address of the reporting device
* `meter_mac_id`: MAC address of the smart meter
* `timestamp`: Time of measurement (UTC)
* `summation_delivered`: Cumulative energy delivered to customer (raw units)
* `summation_received`: Cumulative energy received from customer (raw units)
* `multiplier`: Scaling multiplier
* `divisor`: Scaling divisor
* `digits_right`: Decimal places
* `digits_left`: Significant digits
* `suppress_leading_zero`: Format flag

**Computed Properties:**
* `delivered_kwh`: Returns energy delivered in kWh, calculated as `(summation_delivered * multiplier) / divisor`
* `received_kwh`: Returns energy received in kWh, calculated as `(summation_received * multiplier) / divisor`

**Example Response:**
```json
{
  "device_mac_id": "00:11:22:33:44:55:66:77:88:99:AA:BB:CC",
  "meter_mac_id": "00:11:22:33:44:55:66:77",
  "timestamp": "2024-02-06T19:41:00Z",
  "summation_delivered": 12345678,
  "summation_received": 0,
  "multiplier": 1,
  "divisor": 1000,
  "digits_right": 3,
  "digits_left": 8,
  "suppress_leading_zero": false
}
```

The `delivered_kwh` property converts: `(12345678 * 1) / 1000 = 12345.678 kWh`

## Combined Usage Data

### UsageData

Combined demand and summation snapshot (HTTP API format).

::: meter_reader.models.UsageData
    handler: python

**Fields:**
* `demand`: Real-time power demand (float, already in kW)
* `demand_units`: Unit of demand measurement (typically `"kW"`)
* `demand_timestamp`: Unix timestamp of demand reading
* `summation_received`: Cumulative energy received (float, in kWh)
* `summation_delivered`: Cumulative energy delivered (float, in kWh)
* `summation_units`: Unit of summation measurement (typically `"kWh"`)
* `meter_status`: Current meter connection status (e.g., `"Connected"`, `"Unavailable"`)
* `consumption`: (Optional) Calculated consumption difference

**Computed Properties:**
* `timestamp`: Returns demand measurement time as Python `datetime` object

**Example Response:**
```json
{
  "demand": 2.468,
  "demand_units": "kW",
  "demand_timestamp": 1707251400,
  "summation_received": 0.0,
  "summation_delivered": 12345.678,
  "summation_units": "kWh",
  "meter_status": "Connected",
  "consumption": null
}
```

Note: This model is primarily used by the HTTP API client. Socket API clients may synthesize this from separate demand and summation queries.

## Network Information

### NetworkInfo

ZigBee network status and signal strength.

::: meter_reader.models.NetworkInfo
    handler: python

**Fields:**
* `device_mac_id`: MAC address of the reporting device
* `coord_mac_id`: MAC address of the ZigBee coordinator
* `status`: Network connection status (e.g., `"Connected"`)
* `description`: Status description
* `ext_pan_id`: Extended Personal Area Network ID
* `channel`: ZigBee channel in use (11-26, typically 11-15 in 2.4GHz)
* `short_addr`: Short network address assigned to device
* `link_strength`: Signal strength (0-100, percentage)

**Example Response:**
```json
{
  "device_mac_id": "00:11:22:33:44:55:66:77:88:99:AA:BB:CC",
  "coord_mac_id": "00:0D:6F:00:0A:90:69:E7",
  "status": "Connected",
  "description": "Device is connected",
  "ext_pan_id": "00:0D:6F:FF:FE:00:XX:XX",
  "channel": 15,
  "short_addr": "0x1234",
  "link_strength": 87
}
```

The `link_strength` field is particularly useful for diagnosing ZigBee mesh network issues.

## Usage Patterns

### Accessing Converted Values

All models with raw integer values provide computed properties for convenient unit conversion:

```python
from meter_reader import EagleSocketClient

client = EagleSocketClient("192.168.1.100")

# Get demand with automatic unit conversion
demand = client.get_instantaneous_demand()
print(f"Current power: {demand.panic_demand} kW")  # Already in kW

# Get summation with automatic unit conversion
summation = client.get_current_summation()
print(f"Total energy: {summation.delivered_kwh} kWh")  # Already in kWh
```

### Accessing Raw Values

Raw integer values are also available directly when needed for advanced use cases:

```python
demand = client.get_instantaneous_demand()
raw_demand = demand.demand  # Integer raw value
multiplier = demand.multiplier
divisor = demand.divisor
# Manual calculation: (raw_demand * multiplier) / divisor
```

### Working with Timestamps

All timestamp fields are automatically converted to `datetime` objects:

```python
from meter_reader import EagleSocketClient

client = EagleSocketClient("192.168.1.100")
summation = client.get_current_summation()

# timestamp is a datetime object
print(f"Reading time: {summation.timestamp}")
print(f"ISO format: {summation.timestamp.isoformat()}")
print(f"Unix timestamp: {int(summation.timestamp.timestamp())}")
```
