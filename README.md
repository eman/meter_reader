# Meter Reader

[![License: BSD 2-Clause](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](LICENSE.rst)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

Meter Reader is a client library and command-line tool for retrieving near-realtime energy usage data from a smart meter via the **Eagle™ Home Energy Gateway**. See [Rainforest™ Automation](http://www.rainforestautomation.com) for more information about the Eagle™ Home Energy Gateway.

**Disclaimer**: Meter Reader is not affiliated with the Eagle™ Home Energy Gateway or Rainforest™ Automation.

## Features

- **Library API** - Use as a Python library in your own applications
- **CLI Tool** - Command-line interface for querying gateway data
- **Multiple Commands** - Support for device data, instantaneous demand, and historical values
- **Multiple Formats** - Output in table, JSON, or CSV format
- **Type-Safe** - Full type hints for better IDE support and type checking
- **Modern Packaging** - Built with pyproject.toml and PEP 517 compliance
- **No Dependencies** - Pure Python standard library, no external dependencies

## Installation

### From PyPI

```bash
pip install meter-reader
```

### From Source

```bash
git clone https://github.com/eman/meter_reader.git
cd meter_reader
pip install -e .
```

## Quick Start

### Command-Line Usage

Get help:
```bash
mr --help
```

List devices on gateway:
```bash
mr list 192.168.1.10
```

Get current power demand:
```bash
mr instantaneous 192.168.1.10
```

Get device data:
```bash
mr device-data 192.168.1.10
```

Get summation values for the past day:
```bash
mr summation 192.168.1.10 --interval day
```

### Library Usage

```python
from meter_reader import Gateway

# Connect to gateway
gateway = Gateway('192.168.1.10')

# Get instantaneous demand
timestamp, demand_kw = gateway.get_instantaneous_demand()
print(f'Current demand: {demand_kw}kW at {timestamp}')

# Get device data
response = gateway.run_command(Name='get_device_data')
print(response['CurrentSummation'])

# Get summation values
data = gateway.run_command(
    Name='get_summation_values',
    Interval='day'
)
for entry in data:
    print(f"{entry['TimeStamp']}: {entry['SummationDelivered']}")
```

## CLI Commands

All commands support the following options:

- `-t, --timeout SECONDS` - Socket timeout (default: 5)
- `-f, --output-format {table,json,csv}` - Output format (default: table)
- `-r, --raw` - Display raw XML response
- `--debug` - Enable debug logging

### list

List all devices on the gateway:
```bash
mr list 192.168.1.10
mr list 192.168.1.10 --output-format json
mr list 192.168.1.10 --raw
```

### device-data

Get device data from the gateway:
```bash
mr device-data 192.168.1.10
mr device-data 192.168.1.10 --output-format json
```

### instantaneous

Get current instantaneous power demand:
```bash
mr instantaneous 192.168.1.10
mr instant 192.168.1.10  # short alias
mr instantaneous 192.168.1.10 --output-format json
```

Output:
```
2024-02-01 21:58:39+00:00, 0.292kW
```

### summation

Get summation values for a time period:
```bash
mr summation 192.168.1.10 --interval day
mr summation 192.168.1.10 --interval hour --frequency 900
mr summation 192.168.1.10 --interval week --output-format csv
```

Options:
- `-i, --interval {hour,day,week}` - Time interval (default: day)
- `--frequency SECONDS` - Seconds between samples
- `-s, --start-time TIME` - Start time
- `-e, --end-time TIME` - End time
- `-d, --duration SECONDS` - Duration in seconds

### demand

Get demand values for a time period:
```bash
mr demand 192.168.1.10 --interval day
mr demand 192.168.1.10 --interval week --output-format json
```

Options same as `summation` command.

## Output Formats

### Table (default)

```
MessageCluster
   DeviceMacId          xx:xx:xx:xx:xx:xx:xx:xx
   MeterMacId           xx:xx:xx:xx:xx:xx:xx
   TimeStamp            2024-02-01 21:58:39+00:00
```

### JSON

```bash
mr device-data 192.168.1.10 --output-format json
```

```json
{
  "MessageCluster": {
    "DeviceMacId": "xx:xx:xx:xx:xx:xx:xx:xx",
    "MeterMacId": "xx:xx:xx:xx:xx:xx:xx",
    "TimeStamp": "2024-02-01 21:58:39+00:00"
  }
}
```

### CSV

```bash
mr summation 192.168.1.10 --output-format csv
```

```
MessageCluster.DeviceMacId,xx:xx:xx:xx:xx:xx:xx:xx
MessageCluster.TimeStamp,2024-02-01 21:58:39+00:00
```

## API Reference

### Gateway

```python
from meter_reader import Gateway

gateway = Gateway(address, port=5002, timeout=5)
```

**Parameters:**
- `address` (str): Gateway IP address or hostname
- `port` (int): Gateway port (default: 5002)
- `timeout` (int): Socket timeout in seconds (default: 5)

**Methods:**

#### `run_command(**kwargs)`

Send a command to the gateway and return parsed response.

```python
response = gateway.run_command(Name='list_devices')
response = gateway.run_command(
    Name='get_summation_values',
    Interval='day'
)
```

**Parameters:**
- `Name` (str): Command name
- `convert` (bool): Convert data types (default: True)
- Other parameters depending on command

**Returns:** dict or list of dicts

**Raises:** `GatewayError` on communication failure

#### `run_command_raw(**kwargs)`

Send a command and return raw XML response.

```python
raw_xml = gateway.run_command_raw(Name='get_device_data')
```

#### `get_instantaneous_demand()`

Get current power demand.

```python
timestamp, demand_kw = gateway.get_instantaneous_demand()
```

**Returns:** Tuple of (datetime, float)

### GatewayError

Exception raised when gateway communication fails.

```python
from meter_reader import GatewayError

try:
    gateway = Gateway('192.168.1.10')
except GatewayError as e:
    print(f'Connection failed: {e}')
```

## Supported Commands

The following commands are supported by the gateway:

- `list_devices` - List all devices
- `get_device_data` - Get device data
- `get_instantaneous_demand` - Get current demand
- `get_demand_values` - Get demand history
- `get_summation_values` - Get summation history
- `get_fast_poll_status` - Get fast poll status

## Troubleshooting

### Connection Timeout

If you get a timeout error, try increasing the timeout value:

```bash
mr device-data 192.168.1.10 --timeout 10
```

Or in code:

```python
gateway = Gateway('192.168.1.10', timeout=10)
```

### No Devices Found

If the gateway doesn't have any devices connected, you may get an error. Check that your gateway is properly configured and devices are paired.

### Raw XML Response

To see the raw response from the gateway for debugging:

```bash
mr device-data 192.168.1.10 --raw
```

### Debug Logging

Enable debug logging to see detailed communication:

```bash
mr --debug device-data 192.168.1.10
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/eman/meter_reader.git
cd meter_reader
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy src/
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

## Changes from v1.x

Version 2.0 includes significant improvements:

- **Refactored CLI** with subcommands instead of options
- **Multiple output formats** (table, JSON, CSV)
- **Better error handling** with logging support
- **Modern packaging** with pyproject.toml
- **Improved documentation** with examples
- **Bug fix** for socket handling with proper timeout support
- **Removed OrderedDict** usage (Python 3.7+ dict ordering)
- **Full type hints** throughout codebase

## License

BSD 2-Clause License - See [LICENSE.rst](LICENSE.rst) for details.

Copyright © 2017-2026 Emmanuel Levijarvi

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## See Also

- [Rainforest Automation](http://www.rainforestautomation.com)
- [Eagle Energy Gateway](https://www.rainforestautomation.com/rfa/)

## Support

For issues, questions, or suggestions, please open an issue on [GitHub](https://github.com/eman/meter_reader/issues).
