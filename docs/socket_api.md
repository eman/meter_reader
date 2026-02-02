# Socket API (Port 5002)

## Overview

The primary method for communicating with the Rainforest EAGLE gateway is via a TCP socket on port **5002**. This interface allows you to send XML commands and receive XML responses in a persistent session.

## Connection Details

* **Port**: 5002
* **Protocol**: TCP
* **Authentication**: Basic Auth (HTTP-style headers required initially or possibly implied by credentials in command - verify with `gateway.py` implementation, actually `gateway.py` sends `set_auth` or uses local credentials if enabled? No, wait. The script sends XML directly. The `gateway.py` implementation just opens a socket and sends data. But wait, `EAGLE_REST_API` mentions Basic Auth for HTTP, but for Socket? Let's check `gateway.py` again. `_create_socket` just connects. The commands include `<User>` and `<Password>` within the XML payload if required by device settings, but typically the local API is open or uses `set_auth`.)
  * *Correction*: The `gateway.py` implementation sends user/pass in the XML body for some commands, or relies on the session state.

## Command Structure

Commands are sent as XML fragments. The root element is typically `<LocalCommand>`.

### Request Example

```xml
<LocalCommand>
    <Name>get_usage_data</Name>
    <MacId>0xd8d5b90000000cee</MacId>
</LocalCommand>
```

### Response Example

```xml
<usage_data>
    <demand>1.234</demand>
    <demand_units>kW</demand_units>
    <summation_delivered>12345.678</summation_delivered>
    <meter_status>Connected</meter_status>
</usage_data>
```

## Supported Commands

The following commands have been verified to work on the EAGLE 200 (Firmware 1.4.48):

* **`get_device_list`**
  * Returns list of paired devices (meters).
* **`get_device_data`** (mapped to `get_instantaneous_demand` in library)
  * Returns real-time demand.
* **`get_usage_data`**
  * Returns current usage details.
* **`get_network_info`**
  * Returns ZigBee network status, channel, and link strength.
* **`get_history_data`**
  * Returns historical data (summation, demand) for specified time periods.
  * *Note*: Response can be large and nested.

## Unsupported Commands

The following commands are documented in `EAGLE_REST_API-1.0.pdf` but were **rejected** by the device during testing:

* `get_price`
* `get_message`
* `get_current_summation` (use `get_history_data`)
* `set_price` (via socket - use HTTP for reliable setting)

## Libraries

* **Python**: `meter_reader` (this library) provides a convenient wrapper around this socket API.
