# HTTP API (OpenAPI)

## Overview

The EAGLE Gateway provides a local HTTP API on port 80 that accepts XML commands via POST requests and returns JSON responses. This is an alternative to the Socket API for scenarios requiring standard HTTP communication.

## Authentication

The HTTP API uses **HTTP Basic Authentication**. Include credentials in request headers:

```
Authorization: Basic base64(username:password)
```

Example with curl:

```bash
curl -u admin:password http://192.168.1.100/cgi-bin/cgi_manager \
  -H "Content-Type: text/xml" \
  -d '<LocalCommand><Name>get_usage_data</Name></LocalCommand>'
```

## Endpoints

### Primary Endpoint: /cgi-bin/cgi_manager

Retrieves meter data and device information. Requests are XML-encoded, responses are JSON.

#### Request Format

Send an XML command wrapped in `<LocalCommand>` tags:

```xml
<LocalCommand>
  <Name>get_usage_data</Name>
  <MacId>0xd8d5b90000000cee</MacId>
</LocalCommand>
```

#### Response Format

All responses are JSON objects with snake_case keys:

```json
{
  "demand": "2.468",
  "demand_units": "kW",
  "demand_timestamp": 1707251400,
  "summation_delivered": "12345.678",
  "summation_received": "0.0",
  "summation_units": "kWh",
  "meter_status": "Connected"
}
```

### Supported Commands

#### get_usage_data

Returns combined demand and summation snapshot.

**Request:**
```xml
<LocalCommand>
  <Name>get_usage_data</Name>
</LocalCommand>
```

**Response:**
```json
{
  "demand": "2.468",
  "demand_units": "kW",
  "demand_timestamp": 1707251400,
  "summation_delivered": "12345.678",
  "summation_received": "0.0",
  "summation_units": "kWh",
  "meter_status": "Connected"
}
```

**Fields:**
- `demand`: Real-time power in kW (string, typically 2-3 decimal places)
- `demand_units`: Unit label (always `"kW"`)
- `demand_timestamp`: Unix timestamp of reading
- `summation_delivered`: Total delivered energy in kWh (string)
- `summation_received`: Total received energy in kWh (string)
- `summation_units`: Unit label (always `"kWh"`)
- `meter_status`: Connection status (`"Connected"`, `"Unavailable"`, etc.)

#### get_device_list

Lists all devices (meters) paired with the gateway.

**Request:**
```xml
<LocalCommand>
  <Name>get_device_list</Name>
</LocalCommand>
```

**Response:**
```json
{
  "num_devices": "1",
  "device_mac_id[0]": "00:11:22:33:44:55:66:77:88:99:AA:BB:CC",
  "device_model_id[0]": "EAGLE-200",
  "device_fw_version[0]": "1.4.48"
}
```

**Fields:**
- `num_devices`: Number of paired devices (string)
- `device_mac_id[n]`: MAC address of device n
- `device_model_id[n]`: Model identifier for device n
- `device_fw_version[n]`: Firmware version for device n

#### get_instantaneous_demand

Returns real-time demand only.

**Request:**
```xml
<LocalCommand>
  <Name>get_instantaneous_demand</Name>
  <MacId>0xd8d5b90000000cee</MacId>
</LocalCommand>
```

**Response:**
```json
{
  "demand": "2.468",
  "demand_units": "kW",
  "demand_timestamp": 1707251400
}
```

## Interactive Documentation

The following is an interactive OpenAPI specification viewer where you can explore the API structure and try requests:

!!swagger openapi.yaml!!
