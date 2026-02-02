# Data Models

The library uses Pydantic models to ensure type-safe and consistent data structures across both Socket and HTTP clients.

## Response Models

::: meter_reader.models.DeviceInfo
    handler: python

::: meter_reader.models.DeviceList
    handler: python

::: meter_reader.models.InstantaneousDemand
    handler: python
    options:
      members:
        - panic_demand

::: meter_reader.models.CurrentSummation
    handler: python
    options:
      members:
        - delivered_kwh
        - received_kwh

::: meter_reader.models.UsageData
    handler: python
    options:
      members:
        - timestamp

::: meter_reader.models.NetworkInfo
    handler: python
