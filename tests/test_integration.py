"""Tests for meter_reader package exports and integration."""

import pytest
from meter_reader import (
    EagleSocketClient,
    EagleHttpClient,
    EagleConfigClient,
    InstantaneousDemand,
    UsageData,
    CurrentSummation,
    NetworkInfo,
    DeviceList,
)


class TestPackageExports:
    """Test that all expected classes are exported from main package."""

    def test_socket_client_exported(self):
        """Test EagleSocketClient is exported."""
        assert EagleSocketClient is not None
        assert hasattr(EagleSocketClient, "__init__")

    def test_http_client_exported(self):
        """Test EagleHttpClient is exported."""
        assert EagleHttpClient is not None
        assert hasattr(EagleHttpClient, "__init__")

    def test_config_client_exported(self):
        """Test EagleConfigClient is exported."""
        assert EagleConfigClient is not None
        assert hasattr(EagleConfigClient, "__init__")

    def test_models_exported(self):
        """Test all models are exported."""
        assert InstantaneousDemand is not None
        assert UsageData is not None
        assert CurrentSummation is not None
        assert NetworkInfo is not None
        assert DeviceList is not None

    def test_socket_client_instantiation(self):
        """Test EagleSocketClient can be instantiated."""
        client = EagleSocketClient("192.168.1.100")
        assert client is not None
        assert client.address == ("192.168.1.100", 5002)

    def test_http_client_instantiation(self):
        """Test EagleHttpClient can be instantiated."""
        client = EagleHttpClient("192.168.1.100", "admin", "password")
        assert client is not None
        assert client.base_url == "http://192.168.1.100/cgi-bin/cgi_manager"

    def test_config_client_instantiation(self):
        """Test EagleConfigClient can be instantiated."""
        client = EagleConfigClient("192.168.1.100", "admin", "password")
        assert client is not None
        assert client.base_url == "http://192.168.1.100/cgi-bin/post_manager"

    def test_clients_module_exports(self):
        """Test clients module has all exports."""
        from meter_reader.clients import (
            SocketClient,
            HttpClient,
            ConfigClient,
            EagleClient,
        )
        
        assert SocketClient is not None
        assert HttpClient is not None
        assert ConfigClient is not None
        assert EagleClient is not None


class TestClientCompatibility:
    """Test compatibility and consistency across client types."""

    def test_socket_client_has_required_methods(self):
        """Test Socket client has expected data retrieval methods."""
        client = EagleSocketClient("192.168.1.100")
        assert hasattr(client, "get_instantaneous_demand")
        assert hasattr(client, "get_current_summation")
        assert hasattr(client, "get_usage_data")
        assert hasattr(client, "get_network_info")
        assert hasattr(client, "list_devices")

    def test_http_client_has_required_methods(self):
        """Test HTTP client has expected data retrieval methods."""
        client = EagleHttpClient("192.168.1.100", "admin", "password")
        assert hasattr(client, "get_instantaneous_demand")
        assert hasattr(client, "get_current_summation")
        assert hasattr(client, "get_usage_data")
        assert hasattr(client, "list_devices")

    def test_config_client_has_config_methods(self):
        """Test Config client has expected configuration methods."""
        client = EagleConfigClient("192.168.1.100", "admin", "password")
        assert hasattr(client, "get_mdns_status")
        assert hasattr(client, "set_mdns")
        assert hasattr(client, "get_device_config")
        assert hasattr(client, "get_cloud_status")
        assert hasattr(client, "get_remote_management_status")
        assert hasattr(client, "set_remote_management")
        assert hasattr(client, "get_time_status")
        assert hasattr(client, "get_network_info")
        assert hasattr(client, "get_ssh_status")
        assert hasattr(client, "run_command")

    def test_socket_client_address_format(self):
        """Test Socket client address is formatted as tuple."""
        client = EagleSocketClient("192.168.1.100")
        assert isinstance(client.address, tuple)
        assert len(client.address) == 2
        assert client.address[0] == "192.168.1.100"
        assert client.address[1] == 5002

    def test_socket_client_custom_port(self):
        """Test Socket client with custom port."""
        client = EagleSocketClient("192.168.1.100", port=5003)
        assert client.address == ("192.168.1.100", 5003)

    def test_http_client_url_format(self):
        """Test HTTP client URL is properly formatted."""
        client = EagleHttpClient("192.168.1.100", "admin", "password")
        assert client.base_url.startswith("http://")
        assert "192.168.1.100" in client.base_url
        assert "/cgi-bin/cgi_manager" in client.base_url

    def test_config_client_url_format(self):
        """Test Config client URL is properly formatted."""
        client = EagleConfigClient("192.168.1.100", "admin", "password")
        assert client.base_url.startswith("http://")
        assert "192.168.1.100" in client.base_url
        assert "/cgi-bin/post_manager" in client.base_url

    def test_http_and_config_share_auth(self):
        """Test both HTTP clients use Basic Auth."""
        http = EagleHttpClient("192.168.1.100", "user", "pass")
        config = EagleConfigClient("192.168.1.100", "user", "pass")
        
        assert http.auth == ("user", "pass")
        assert config.auth == ("user", "pass")
