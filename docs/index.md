# EAGLE Meter Reader

Welcome to the documentation for the `meter_reader` library.

## Introduction

This library provides a Python interface to the **Rainforest EAGLE 200 Gateway**. It allows you to retrieve real-time energy usage data, historical consumption, and network information from your smart meter via the gateway.

## Features

* **Real-time Data**: Fetch instantaneous demand and summation.
* **Historical Data**: Retrieve past usage logs.
* **Device Management**: Configure settings (price, cloud provider, etc.).
* **Two Interfaces**: Support for both the robust Socket API (legacy) and the modern HTTP API (JSON).

## Installation

```bash
pip install meter_reader
```

## Quick Start

```python
from meter_reader import EagleSocketClient

client = EagleSocketClient("10.0.0.247")
data = client.get_instantaneous_demand()
print(f"Current Demand: {data.panic_demand} kW")
```

## CLI Usage

The library includes a command-line interface (`mr`) powered by Typer.

```bash
# Get demand via Socket API (default)
mr demand 10.0.0.247

# Get usage via HTTP API
mr usage 10.0.0.247 --protocol http --username <user> --password <pass>
```
