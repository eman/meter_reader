"""Tests for meter_reader configuration client module."""

from unittest.mock import patch, MagicMock
import pytest
import requests

from meter_reader.clients.config import EagleConfigClient


class TestEagleConfigClient:
    """Test EagleConfigClient class."""

    def test_client_initialization(self):
        """Test client initialization with address, username, password."""
        client = EagleConfigClient("192.168.1.100", "admin", "password")
        assert client.base_url == "http://192.168.1.100/cgi-bin/post_manager"
        assert client.auth == ("admin", "password")
        assert client.timeout == 10

    def test_client_initialization_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = EagleConfigClient("192.168.1.100", "admin", "password", timeout=30)
        assert client.timeout == 30

    @patch("meter_reader.clients.config.requests.post")
    def test_get_mdns_status(self, mock_post):
        """Test get_mdns_status method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "mDnsStatus": {
                "Enabled": "Y",
                "Hostname": "eagle-000cee",
                "Status": "Active"
            }
        }
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.get_mdns_status()

        assert result["mDnsStatus"]["Enabled"] == "Y"
        assert result["mDnsStatus"]["Hostname"] == "eagle-000cee"
        mock_post.assert_called_once()
        
        # Verify XML structure
        call_args = mock_post.call_args
        xml_data = call_args[1]["data"]
        assert "<Name>get_mdns_status</Name>" in xml_data
        assert "<Format>JSON</Format>" in xml_data

    @patch("meter_reader.clients.config.requests.post")
    def test_set_mdns_enabled(self, mock_post):
        """Test set_mdns with enabled=True."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": "OK"}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.set_mdns(enabled=True)

        assert result["Status"] == "OK"
        call_args = mock_post.call_args
        xml_data = call_args[1]["data"]
        assert "<Name>set_mdns</Name>" in xml_data
        assert "<Enabled>Y</Enabled>" in xml_data

    @patch("meter_reader.clients.config.requests.post")
    def test_set_mdns_disabled(self, mock_post):
        """Test set_mdns with enabled=False."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": "OK"}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.set_mdns(enabled=False)

        assert result["Status"] == "OK"
        call_args = mock_post.call_args
        xml_data = call_args[1]["data"]
        assert "<Enabled>N</Enabled>" in xml_data

    @patch("meter_reader.clients.config.requests.post")
    def test_get_device_config(self, mock_post):
        """Test get_device_config method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "FirmwareVersion": "1.4.48",
            "HardwareVersion": "2.0",
            "MacAddress": "00:0D:6F:00:0A:90:69:E7",
            "ModelID": "EAGLE-200",
            "ManufacturerID": "Rainforest Automation",
            "UpdateStatus": "Current",
            "UpdateAvailable": "N"
        }
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.get_device_config()

        assert result["FirmwareVersion"] == "1.4.48"
        assert result["HardwareVersion"] == "2.0"
        assert result["UpdateAvailable"] == "N"
        mock_post.assert_called_once()

    @patch("meter_reader.clients.config.requests.post")
    def test_get_cloud_status(self, mock_post):
        """Test get_cloud_status method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "CloudStatus": {
                "Connected": "Y",
                "Provider": "Rainforest",
                "LastUpdate": "2024-02-06T20:08:43Z",
                "AccountStatus": "Active"
            }
        }
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.get_cloud_status()

        assert result["CloudStatus"]["Connected"] == "Y"
        assert result["CloudStatus"]["Provider"] == "Rainforest"

    @patch("meter_reader.clients.config.requests.post")
    def test_get_remote_management_status(self, mock_post):
        """Test get_remote_management_status method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "RemoteEnabled": "Y",
            "RemoteStatus": "Connected",
            "LastConnection": "2024-02-06T20:05:00Z",
            "Provider": "Rainforest"
        }
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.get_remote_management_status()

        assert result["RemoteEnabled"] == "Y"
        assert result["RemoteStatus"] == "Connected"

    @patch("meter_reader.clients.config.requests.post")
    def test_set_remote_management_enabled(self, mock_post):
        """Test set_remote_management with enabled=True."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": "OK"}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.set_remote_management(enabled=True)

        assert result["Status"] == "OK"
        call_args = mock_post.call_args
        xml_data = call_args[1]["data"]
        assert "<Name>set_remote_management</Name>" in xml_data
        assert "<Enabled>Y</Enabled>" in xml_data

    @patch("meter_reader.clients.config.requests.post")
    def test_set_remote_management_disabled(self, mock_post):
        """Test set_remote_management with enabled=False."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": "OK"}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        client.set_remote_management(enabled=False)

        call_args = mock_post.call_args
        xml_data = call_args[1]["data"]
        assert "<Enabled>N</Enabled>" in xml_data

    @patch("meter_reader.clients.config.requests.post")
    def test_get_ssh_status(self, mock_post):
        """Test get_ssh_status method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "SshEnabled": "N",
            "SshStatus": "Disabled"
        }
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.get_ssh_status()

        assert result["SshEnabled"] == "N"
        mock_post.assert_called_once()

    @patch("meter_reader.clients.config.requests.post")
    def test_get_time_status(self, mock_post):
        """Test get_time_status method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "CurrentTime": "2024-02-06T20:08:43Z",
            "NtpStatus": "Synchronized",
            "NtpServer": "pool.ntp.org",
            "TimeZone": "UTC",
            "DaylightSavings": "N"
        }
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.get_time_status()

        assert result["NtpStatus"] == "Synchronized"
        assert result["TimeZone"] == "UTC"

    @patch("meter_reader.clients.config.requests.post")
    def test_get_network_info(self, mock_post):
        """Test get_network_info method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "IPAddress": "192.168.1.100",
            "Netmask": "255.255.255.0",
            "Gateway": "192.168.1.1",
            "DNS1": "192.168.1.1",
            "DNS2": "8.8.8.8",
            "DHCP": "Y",
            "Hostname": "eagle-000cee"
        }
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.get_network_info()

        assert result["IPAddress"] == "192.168.1.100"
        assert result["DHCP"] == "Y"
        assert result["Hostname"] == "eagle-000cee"

    @patch("meter_reader.clients.config.requests.post")
    def test_run_command(self, mock_post):
        """Test run_command with arbitrary command name."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Result": "Success"}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.run_command("get_mdns_status")

        assert result["Result"] == "Success"
        mock_post.assert_called_once()

    @patch("meter_reader.clients.config.requests.post")
    def test_run_command_with_parameters(self, mock_post):
        """Test run_command with additional parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": "OK"}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        client.run_command("some_command", Param1="value1", Param2="value2")

        call_args = mock_post.call_args
        xml_data = call_args[1]["data"]
        assert "<Param1>value1</Param1>" in xml_data
        assert "<Param2>value2</Param2>" in xml_data

    @patch("meter_reader.clients.config.requests.post")
    def test_post_command_http_error(self, mock_post):
        """Test error handling when HTTP request fails."""
        mock_post.side_effect = requests.RequestException("Connection error")

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        
        with pytest.raises(requests.RequestException):
            client.get_mdns_status()

    @patch("meter_reader.clients.config.requests.post")
    def test_post_command_raises_for_status(self, mock_post):
        """Test error handling for HTTP status errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        
        with pytest.raises(requests.HTTPError):
            client.get_mdns_status()

    @patch("meter_reader.clients.config.requests.post")
    def test_xml_command_structure(self, mock_post):
        """Test XML command is properly formatted."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        client.get_mdns_status()

        call_args = mock_post.call_args
        xml_data = call_args[1]["data"]
        
        # Verify XML structure
        assert xml_data.startswith("<Command>")
        assert xml_data.strip().endswith("</Command>")
        assert "<Name>get_mdns_status</Name>" in xml_data
        assert "<Format>JSON</Format>" in xml_data

    @patch("meter_reader.clients.config.requests.post")
    def test_authentication_passed_to_request(self, mock_post):
        """Test authentication credentials are passed to request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "user", "pass")
        client.get_mdns_status()

        call_args = mock_post.call_args
        assert call_args[1]["auth"] == ("user", "pass")

    @patch("meter_reader.clients.config.requests.post")
    def test_timeout_passed_to_request(self, mock_post):
        """Test timeout is passed to request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password", timeout=25)
        client.get_mdns_status()

        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 25

    @patch("meter_reader.clients.config.requests.post")
    def test_content_type_header(self, mock_post):
        """Test Content-Type header is set to text/xml."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        client.get_mdns_status()

        call_args = mock_post.call_args
        assert call_args[1]["headers"]["Content-Type"] == "text/xml"

    @patch("meter_reader.clients.config.requests.post")
    def test_url_format(self, mock_post):
        """Test post_manager URL is correctly formed."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.50", "admin", "password")
        client.get_mdns_status()

        call_args = mock_post.call_args
        assert call_args[0][0] == "http://192.168.1.50/cgi-bin/post_manager"

    @patch("meter_reader.clients.config.requests.post")
    def test_none_parameter_excluded(self, mock_post):
        """Test None parameters are excluded from XML."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        client.run_command("test_cmd", Param1="value", Param2=None, Param3="value3")

        call_args = mock_post.call_args
        xml_data = call_args[1]["data"]
        assert "<Param1>value</Param1>" in xml_data
        assert "<Param2>" not in xml_data
        assert "<Param3>value3</Param3>" in xml_data

    @patch("meter_reader.clients.config.requests.post")
    def test_json_response_parsing(self, mock_post):
        """Test JSON response is properly parsed."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "NestedData": {
                "Key1": "Value1",
                "Key2": "Value2"
            }
        }
        mock_post.return_value = mock_response

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        result = client.run_command("test")

        assert result["NestedData"]["Key1"] == "Value1"
        assert result["NestedData"]["Key2"] == "Value2"

    @patch("meter_reader.clients.config.requests.post")
    def test_multiple_calls_independent(self, mock_post):
        """Test multiple calls maintain independent state."""
        mock_responses = []
        for result in ["First", "Second", "Third"]:
            mock_response = MagicMock()
            mock_response.json.return_value = {"Result": result}
            mock_responses.append(mock_response)
        
        mock_post.side_effect = mock_responses

        client = EagleConfigClient("192.168.1.100", "admin", "password")
        
        result1 = client.get_mdns_status()
        result2 = client.get_device_config()
        result3 = client.get_network_info()

        assert result1["Result"] == "First"
        assert result2["Result"] == "Second"
        assert result3["Result"] == "Third"
        assert mock_post.call_count == 3
