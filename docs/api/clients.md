# Clients API

The `meter_reader` library provides two client implementations for the Eagle Gateway.

## Base Client

::: meter_reader.clients.base.EagleClient
    handler: python
    options:
      members:
        - get_instantaneous_demand
        - get_usage_data
        - list_devices
        - get_network_info
        - get_current_summation

## Socket Client

The `EagleSocketClient` communicates via the local XML API on port 5002. This is the traditional method for most integrations.

::: meter_reader.clients.socket.EagleSocketClient
    handler: python
    options:
      members:
        - __init__
        - list_devices
        - get_instantaneous_demand
        - get_history_data

## HTTP Client

The `EagleHttpClient` communicates via the local web interface API (`cgi_manager`) on port 80. This method uses JSON responses where possible and supports username/password authentication.

::: meter_reader.clients.http.EagleHttpClient
    handler: python
    options:
      members:
        - __init__
        - get_usage_data
        - list_devices
