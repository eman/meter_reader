"""Tests for meter_reader socket client module."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
import socket

from meter_reader.clients.socket import (
    EagleSocketClient,
    GatewayError,
    twos_complement,
    convert_data,
    BEGINNING_OF_TIME,
)
from meter_reader.models import (
    DeviceList,
    InstantaneousDemand,
    CurrentSummation,
    NetworkInfo,
    UsageData,
)


class TestTwosComplement:
    """Test twos_complement helper function."""

    def test_positive_value(self):
        """Test positive value remains positive."""
        assert twos_complement(100) == 100

    def test_negative_value_32bit(self):
        """Test negative value conversion (32-bit)."""
        # 0xFFFFFFFF should be -1
        assert twos_complement(0xFFFFFFFF, 32) == -1

    def test_negative_value_16bit(self):
        """Test negative value conversion (16-bit)."""
        # 0xFFFF should be -1 in 16-bit
        assert twos_complement(0xFFFF, 16) == -1

    def test_max_positive(self):
        """Test max positive value for 32-bit."""
        # 0x7FFFFFFF is max positive for 32-bit signed
        assert twos_complement(0x7FFFFFFF, 32) == 0x7FFFFFFF


class TestConvertData:
    """Test convert_data helper function."""

    def test_mac_id_conversion(self):
        """Test MAC ID formatting with colons."""
        result = convert_data("DeviceMacId", "0xd8d5b9000000abcd")
        assert result == "d8:d5:b9:00:00:00:ab:cd"

    def test_meter_mac_id_shorter(self):
        """Test MeterMacId has shorter format."""
        result = convert_data("MeterMacId", "0xd8d5b9000000ab")
        assert result == "d8:d5:b9:00:00:00:ab"

    def test_timestamp_conversion(self):
        """Test timestamp conversion from hex offset."""
        # 3600 seconds after 2000-01-01
        result = convert_data("TimeStamp", "0xe10")
        expected = BEGINNING_OF_TIME + timedelta(seconds=3600)
        assert result == expected

    def test_hex_value_conversion(self):
        """Test hex value conversion to integer."""
        result = convert_data("SomeValue", "0x64")
        assert result == 100

    def test_negative_hex_value(self):
        """Test negative hex value using two's complement."""
        result = convert_data("SomeValue", "0xFFFFFFFF")
        assert result == -1

    def test_none_value(self):
        """Test None value returns None."""
        assert convert_data("Test", None) is None

    def test_non_hex_string(self):
        """Test non-hex string passes through."""
        result = convert_data("Description", "Connected")
        assert result == "Connected"


class TestGatewayError:
    """Test GatewayError exception."""

    def test_error_creation(self):
        """Test creating GatewayError."""
        error = GatewayError(
            ("192.168.1.1", 5002), "list_devices", "Connection refused"
        )
        assert error.address == ("192.168.1.1", 5002)
        assert error.command == "list_devices"
        assert error.error == "Connection refused"

    def test_error_string(self):
        """Test error string representation."""
        error = GatewayError(("192.168.1.1", 5002), "test", "Network error")
        assert "192.168.1.1:5002" in str(error)
        assert "Network error" in str(error)


class TestEagleSocketClient:
    """Test EagleSocketClient class."""

    def test_client_initialization_with_device_list(self):
        """Test client initializes and handles MAC ID."""
        # The client tries to auto-discover MAC ID, which will fail
        # in the test environment, so it should gracefully handle the exception
        client = EagleSocketClient("192.168.1.1")
        # After initialization, mac_id should be None since we can't connect
        assert client.mac_id is None
        # But we can manually set it
        client.mac_id = "0xd8d5b9000000abcd"
        assert client.mac_id == "0xd8d5b9000000abcd"

    @patch("meter_reader.clients.socket.EagleSocketClient._fetch_device_list")
    def test_client_initialization_failure(self, mock_fetch):
        """Test client handles initialization failure gracefully."""
        mock_fetch.side_effect = Exception("Connection refused")

        # Should not raise, but log warning
        client = EagleSocketClient("192.168.1.1")
        assert client.mac_id is None

    def test_generate_command_xml(self):
        """Test XML command generation."""
        client = EagleSocketClient.__new__(EagleSocketClient)
        client.mac_id = "0xabcd"

        xml = client.generate_command_xml(Name="test")
        assert "<Name>test</Name>" in xml
        assert "<MacID>0xabcd</MacID>" in xml

    def test_xml2dict_simple(self):
        """Test parsing simple XML to dict."""
        client = EagleSocketClient.__new__(EagleSocketClient)
        xml = "<response><Status>Connected</Status></response>"
        result = client._xml2dict(xml, convert=False)
        assert result["Status"] == "Connected"

    def test_xml2dict_nested(self):
        """Test parsing nested XML."""
        client = EagleSocketClient.__new__(EagleSocketClient)
        xml = """<response>
            <DeviceInfo>
                <DeviceMacId>0xabcd</DeviceMacId>
                <ModelId>Z109-EAGLE</ModelId>
            </DeviceInfo>
        </response>"""
        result = client._xml2dict(xml, convert=False)
        assert "DeviceInfo" in result
        assert result["DeviceInfo"]["DeviceMacId"] == "0xabcd"

    def test_xml2dict_list_detection(self):
        """Test XML parser detects lists from repeated tags."""
        client = EagleSocketClient.__new__(EagleSocketClient)
        xml = """<response>
            <HistoryData>
                <CurrentSummation>
                    <TimeStamp>0x0</TimeStamp>
                </CurrentSummation>
                <CurrentSummation>
                    <TimeStamp>0x100</TimeStamp>
                </CurrentSummation>
            </HistoryData>
        </response>"""
        result = client._xml2dict(xml, convert=False)
        assert "HistoryData" in result
        assert isinstance(result["HistoryData"]["CurrentSummation"], list)
        assert len(result["HistoryData"]["CurrentSummation"]) == 2

    def test_xml2dict_empty_string(self):
        """Test parsing empty XML string."""
        client = EagleSocketClient.__new__(EagleSocketClient)
        result = client._xml2dict("", convert=False)
        assert result == {}

    def test_xml2dict_invalid_xml(self):
        """Test parsing invalid XML."""
        client = EagleSocketClient.__new__(EagleSocketClient)
        result = client._xml2dict("<invalid", convert=False)
        assert result == {}

    @patch("meter_reader.clients.socket.socket.create_connection")
    def test_run_command_raw(self, mock_connect):
        """Test running raw command."""
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b"<response>test</response>", b""]
        mock_connect.return_value = mock_socket

        client = EagleSocketClient.__new__(EagleSocketClient)
        client.address = ("192.168.1.1", 5002)
        client.timeout = 5
        client.mac_id = None

        result = client._run_command_raw(Name="test")
        assert "<response>test</response>" in result

    @patch("meter_reader.clients.socket.socket.create_connection")
    def test_run_command_socket_error(self, mock_connect):
        """Test socket error handling."""
        mock_connect.side_effect = socket.error("Connection refused")

        client = EagleSocketClient.__new__(EagleSocketClient)
        client.address = ("192.168.1.1", 5002)
        client.timeout = 5
        client.mac_id = None

        with pytest.raises(GatewayError) as exc_info:
            client._run_command_raw(Name="test")
        assert "Connection refused" in str(exc_info.value)

    @patch("meter_reader.clients.socket.EagleSocketClient._run_command_dict")
    def test_list_devices(self, mock_run):
        """Test list_devices method."""
        mock_run.return_value = {
            "DeviceInfo": {
                "DeviceMacId": "0xd8d5b9000000abcd",
                "ModelId": "Z109-EAGLE",
            }
        }

        client = EagleSocketClient.__new__(EagleSocketClient)
        result = client.list_devices()

        assert isinstance(result, DeviceList)
        assert len(result.device_info) == 1
        assert result.device_info[0].device_mac_id == "0xd8d5b9000000abcd"

    @patch("meter_reader.clients.socket.EagleSocketClient._run_command_dict")
    def test_get_instantaneous_demand(self, mock_run):
        """Test get_instantaneous_demand method."""
        mock_run.return_value = {
            "InstantaneousDemand": {
                "DeviceMacId": "d8:d5:b9:00:00:00:ab:cd",
                "MeterMacId": "d8:d5:b9:00:00:ab",
                "TimeStamp": datetime.now(timezone.utc),
                "Demand": 1000,
                "Multiplier": 1,
                "Divisor": 1000,
                "DigitsRight": 3,
                "DigitsLeft": 0,
                "SuppressLeadingZero": False,
            }
        }

        client = EagleSocketClient.__new__(EagleSocketClient)
        client.mac_id = "0xabcd"
        result = client.get_instantaneous_demand()

        assert isinstance(result, InstantaneousDemand)
        assert result.panic_demand == 1.0

    @patch("meter_reader.clients.socket.EagleSocketClient._run_command_dict")
    def test_get_current_summation(self, mock_run):
        """Test get_current_summation method."""
        mock_run.return_value = {
            "CurrentSummation": {
                "DeviceMacId": "d8:d5:b9:00:00:00:ab:cd",
                "MeterMacId": "d8:d5:b9:00:00:ab",
                "TimeStamp": datetime.now(timezone.utc),
                "SummationDelivered": 123456,
                "SummationReceived": 0,
                "Multiplier": 1,
                "Divisor": 1000,
                "DigitsRight": 3,
                "DigitsLeft": 0,
                "SuppressLeadingZero": False,
            }
        }

        client = EagleSocketClient.__new__(EagleSocketClient)
        client.mac_id = "0xabcd"
        result = client.get_current_summation()

        assert isinstance(result, CurrentSummation)
        assert result.delivered_kwh == 123.456

    @patch("meter_reader.clients.socket.EagleSocketClient._run_command_dict")
    def test_get_network_info(self, mock_run):
        """Test get_network_info method."""
        mock_run.return_value = {
            "NetworkInfo": {
                "DeviceMacId": "d8:d5:b9:00:00:00:ab:cd",
                "CoordMacId": "d8:d5:b9:00:00:ab",
                "Status": "Connected",
                "Description": "Zigbee Network",
                "ExtPanId": "0x1234567890ABCDEF",
                "Channel": 15,
                "ShortAddr": "0x1234",
                "LinkStrength": 100,
            }
        }

        client = EagleSocketClient.__new__(EagleSocketClient)
        client.mac_id = "0xabcd"
        result = client.get_network_info()

        assert isinstance(result, NetworkInfo)
        assert result.status == "Connected"

    @patch("meter_reader.clients.socket.EagleSocketClient.get_instantaneous_demand")
    @patch("meter_reader.clients.socket.EagleSocketClient.get_current_summation")
    def test_get_usage_data(self, mock_summation, mock_demand):
        """Test get_usage_data synthesizes from demand and summation."""
        mock_demand.return_value = InstantaneousDemand(
            DeviceMacId="test",
            MeterMacId="test",
            TimeStamp=datetime(2021, 1, 1, tzinfo=timezone.utc),
            Demand=2500,
            Multiplier=1,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=0,
            SuppressLeadingZero=False,
        )
        mock_summation.return_value = CurrentSummation(
            DeviceMacId="test",
            MeterMacId="test",
            TimeStamp=datetime(2021, 1, 1, tzinfo=timezone.utc),
            SummationDelivered=100000,
            SummationReceived=50000,
            Multiplier=1,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=0,
            SuppressLeadingZero=False,
        )

        client = EagleSocketClient.__new__(EagleSocketClient)
        result = client.get_usage_data()

        assert isinstance(result, UsageData)
        assert result.demand == 2500
        assert result.summation_delivered == 100.0
        assert result.summation_received == 50.0

    @patch("meter_reader.clients.socket.EagleSocketClient._run_command_dict")
    def test_get_history_data(self, mock_run):
        """Test get_history_data method."""
        mock_run.return_value = {
            "HistoryData": {
                "CurrentSummation": [
                    {
                        "DeviceMacId": "test",
                        "MeterMacId": "test",
                        "TimeStamp": datetime.now(timezone.utc),
                        "SummationDelivered": 100000,
                        "SummationReceived": 0,
                        "Multiplier": 1,
                        "Divisor": 1000,
                        "DigitsRight": 3,
                        "DigitsLeft": 0,
                        "SuppressLeadingZero": False,
                    }
                ]
            }
        }

        client = EagleSocketClient.__new__(EagleSocketClient)
        client.mac_id = "0xabcd"
        result = client.get_history_data()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], CurrentSummation)

    @patch("meter_reader.clients.socket.EagleSocketClient._run_command_dict")
    def test_get_history_data_empty(self, mock_run):
        """Test get_history_data with no data."""
        mock_run.return_value = {}

        client = EagleSocketClient.__new__(EagleSocketClient)
        client.mac_id = "0xabcd"
        result = client.get_history_data()

        assert result == []
