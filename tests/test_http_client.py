"""Tests for meter_reader HTTP client module."""
import pytest
from unittest.mock import patch, MagicMock
import requests

from meter_reader.clients.http import EagleHttpClient
from meter_reader.models import (
    DeviceList,
    UsageData,
    InstantaneousDemand,
    CurrentSummation,
)


class TestEagleHttpClient:
    """Test EagleHttpClient class."""

    @patch("meter_reader.clients.http.requests.post")
    def test_client_initialization(self, mock_post):
        """Test client initialization with auto MAC detection."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "num_devices": "1",
            "device_mac_id[0]": "0xd8d5b9000000abcd",
            "device_model_id[0]": "Z109-EAGLE",
        }
        mock_post.return_value = mock_response

        client = EagleHttpClient("192.168.1.1", "admin", "password")
        assert client.base_url == "http://192.168.1.1/cgi-bin/cgi_manager"
        assert client.auth == ("admin", "password")
        assert client.mac_id == "0xd8d5b9000000abcd"

    @patch("meter_reader.clients.http.requests.post")
    def test_client_initialization_failure(self, mock_post):
        """Test client handles initialization failure gracefully."""
        mock_post.side_effect = requests.RequestException("Connection error")

        # Should not raise
        client = EagleHttpClient("192.168.1.1", "admin", "password")
        assert client.mac_id is None

    @patch("meter_reader.clients.http.requests.post")
    def test_list_devices(self, mock_post):
        """Test list_devices method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "num_devices": "2",
            "device_mac_id[0]": "0xd8d5b9000000abcd",
            "device_model_id[0]": "Z109-EAGLE",
            "device_mac_id[1]": "0xd8d5b9000000abce",
            "device_model_id[1]": "Z110-EAGLE",
        }
        mock_post.return_value = mock_response

        client = EagleHttpClient.__new__(EagleHttpClient)
        client.base_url = "http://192.168.1.1/cgi-bin/cgi_manager"
        client.auth = ("admin", "password")
        client.timeout = 10
        client.mac_id = None

        result = client.list_devices()

        assert isinstance(result, DeviceList)
        assert len(result.device_info) == 2
        assert result.device_info[0].device_mac_id == "0xd8d5b9000000abcd"
        assert result.device_info[1].model_id == "Z110-EAGLE"
        # MAC ID should be set from first device
        assert client.mac_id == "0xd8d5b9000000abcd"

    @patch("meter_reader.clients.http.requests.post")
    def test_list_devices_empty(self, mock_post):
        """Test list_devices with no devices."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"num_devices": "0"}
        mock_post.return_value = mock_response

        client = EagleHttpClient.__new__(EagleHttpClient)
        client.base_url = "http://192.168.1.1/cgi-bin/cgi_manager"
        client.auth = ("admin", "password")
        client.timeout = 10
        client.mac_id = None

        result = client.list_devices()

        assert isinstance(result, DeviceList)
        assert len(result.device_info) == 0

    @patch("meter_reader.clients.http.requests.post")
    def test_get_usage_data(self, mock_post):
        """Test get_usage_data method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "demand": 2.5,
            "demand_units": "kW",
            "demand_timestamp": 1609459200,
            "summation_delivered": 100.5,
            "summation_received": 10.0,
            "summation_units": "kWh",
            "meter_status": "Connected",
        }
        mock_post.return_value = mock_response

        client = EagleHttpClient.__new__(EagleHttpClient)
        client.base_url = "http://192.168.1.1/cgi-bin/cgi_manager"
        client.auth = ("admin", "password")
        client.timeout = 10
        client.mac_id = "0xabcd"

        result = client.get_usage_data()

        assert isinstance(result, UsageData)
        assert result.demand == 2.5
        assert result.summation_delivered == 100.5
        assert result.meter_status == "Connected"

    @patch("meter_reader.clients.http.EagleHttpClient.get_usage_data")
    def test_get_instantaneous_demand(self, mock_usage):
        """Test get_instantaneous_demand synthesized from usage data."""
        mock_usage.return_value = UsageData(
            demand=2.5,
            demand_units="kW",
            demand_timestamp=1609459200,
            summation_delivered=100.5,
            summation_received=10.0,
            summation_units="kWh",
            meter_status="Connected",
        )

        client = EagleHttpClient.__new__(EagleHttpClient)
        client.mac_id = "0xd8d5b9000000abcd"

        result = client.get_instantaneous_demand()

        assert isinstance(result, InstantaneousDemand)
        assert result.demand == 2.5
        assert result.device_mac_id == "0xd8d5b9000000abcd"
        # Check that multiplier/divisor are set for normalized values
        assert result.multiplier == 1
        assert result.divisor == 1

    @patch("meter_reader.clients.http.EagleHttpClient.get_usage_data")
    def test_get_current_summation(self, mock_usage):
        """Test get_current_summation synthesized from usage data."""
        mock_usage.return_value = UsageData(
            demand=2.5,
            demand_units="kW",
            demand_timestamp=1609459200,
            summation_delivered=100.5,
            summation_received=10.0,
            summation_units="kWh",
            meter_status="Connected",
        )

        client = EagleHttpClient.__new__(EagleHttpClient)
        client.mac_id = "0xd8d5b9000000abcd"

        result = client.get_current_summation()

        assert isinstance(result, CurrentSummation)
        # Values should be converted back to integers with proper divisor
        assert result.summation_delivered == 100500  # 100.5 * 1000
        assert result.summation_received == 10000  # 10.0 * 1000
        assert result.divisor == 1000
        # Check calculated property
        assert result.delivered_kwh == 100.5
        assert result.received_kwh == 10.0

    def test_get_network_info_not_implemented(self):
        """Test get_network_info raises NotImplementedError."""
        client = EagleHttpClient.__new__(EagleHttpClient)
        client.mac_id = "0xabcd"

        with pytest.raises(NotImplementedError):
            client.get_network_info()

    @patch("meter_reader.clients.http.requests.post")
    def test_post_xml_error_handling(self, mock_post):
        """Test HTTP error handling in _post_xml."""
        mock_post.side_effect = requests.RequestException("HTTP 500 Error")

        client = EagleHttpClient.__new__(EagleHttpClient)
        client.base_url = "http://192.168.1.1/cgi-bin/cgi_manager"
        client.auth = ("admin", "password")
        client.timeout = 10
        client.mac_id = "0xabcd"

        with pytest.raises(requests.RequestException):
            client._post_xml("test_command")

    @patch("meter_reader.clients.http.requests.post")
    def test_authentication(self, mock_post):
        """Test that authentication credentials are used."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"num_devices": "0"}
        mock_post.return_value = mock_response

        client = EagleHttpClient.__new__(EagleHttpClient)
        client.base_url = "http://192.168.1.1/cgi-bin/cgi_manager"
        client.auth = ("testuser", "testpass")
        client.timeout = 10
        client.mac_id = "0xabcd"

        client.list_devices()

        # Verify auth was passed to requests.post
        mock_post.assert_called()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["auth"] == ("testuser", "testpass")

    @patch("meter_reader.clients.http.requests.post")
    def test_timeout_setting(self, mock_post):
        """Test that timeout is properly set."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"num_devices": "0"}
        mock_post.return_value = mock_response

        client = EagleHttpClient.__new__(EagleHttpClient)
        client.base_url = "http://192.168.1.1/cgi-bin/cgi_manager"
        client.auth = ("admin", "password")
        client.timeout = 30
        client.mac_id = "0xabcd"

        client.list_devices()

        # Verify timeout was passed
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == 30
