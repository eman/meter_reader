"""Tests for meter_reader utils module."""
import pytest
from datetime import datetime, timezone
from meter_reader.utils import generate_command_xml, BEGINNING_OF_TIME


class TestGenerateCommandXml:
    """Test generate_command_xml function."""

    def test_simple_command(self):
        """Test generating simple command with name only."""
        xml = generate_command_xml(None, Name="list_devices")
        assert "<Name>list_devices</Name>" in xml
        assert "<?xml" in xml

    def test_command_with_mac_id(self):
        """Test command with MAC ID parameter."""
        mac_id = "0xd8d5b9000000abcd"
        xml = generate_command_xml(mac_id, Name="get_device_data")
        assert "<Name>get_device_data</Name>" in xml
        assert f"<MacID>{mac_id}</MacID>" in xml

    def test_mac_id_not_added_when_explicit(self):
        """Test that MAC ID is not auto-added when explicitly provided."""
        mac_id = "0xd8d5b9000000abcd"
        explicit_mac = "0xd8d5b9000000abce"
        xml = generate_command_xml(mac_id, Name="test", DeviceMacId=explicit_mac)
        # Should contain explicit MAC, not auto-added one
        assert f"<DeviceMacId>{explicit_mac}</DeviceMacId>" in xml
        # Should NOT have auto-added MacID
        assert xml.count("MacID") == 0

    def test_datetime_conversion_to_hex(self):
        """Test that datetime values are converted to hex."""
        start_time = BEGINNING_OF_TIME
        xml = generate_command_xml(None, Name="test", StartTime=start_time)
        # Start time at beginning should be 0x0
        assert "<StartTime>0x0</StartTime>" in xml

    def test_datetime_offset_calculation(self):
        """Test datetime offset calculation."""
        from datetime import timedelta
        
        # 1 hour after beginning of time
        one_hour_later = BEGINNING_OF_TIME + timedelta(hours=1)
        xml = generate_command_xml(None, Name="test", StartTime=one_hour_later)
        # 1 hour = 3600 seconds = 0xe10
        assert "<StartTime>0xe10</StartTime>" in xml

    def test_frequency_hex_conversion(self):
        """Test frequency parameter is converted to hex."""
        xml = generate_command_xml(None, Name="test", Frequency=900)
        # 900 decimal = 0x384
        assert "<Frequency>0x384</Frequency>" in xml

    def test_duration_hex_conversion(self):
        """Test duration parameter is converted to hex."""
        xml = generate_command_xml(None, Name="test", Duration=3600)
        # 3600 decimal = 0xe10
        assert "<Duration>0xe10</Duration>" in xml

    def test_unsupported_args_filtered(self):
        """Test that unsupported arguments are filtered out."""
        xml = generate_command_xml(None, Name="test", UnsupportedArg="value")
        assert "UnsupportedArg" not in xml

    def test_none_values_filtered(self):
        """Test that None values are filtered out."""
        xml = generate_command_xml(None, Name="test", Interval=None)
        assert "Interval" not in xml

    def test_multiple_supported_args(self):
        """Test command with multiple supported arguments."""
        xml = generate_command_xml(
            None,
            Name="test_command",
            Frequency=60,
            Enabled="Y",
            Protocol="TCP",
        )
        assert "<Name>test_command</Name>" in xml
        assert "<Frequency>0x3c</Frequency>" in xml  # 60 = 0x3c
        assert "<Enabled>Y</Enabled>" in xml
        assert "<Protocol>TCP</Protocol>" in xml

    def test_case_insensitive_arg_matching(self):
        """Test that argument matching is case-insensitive."""
        xml = generate_command_xml(None, Name="test", macid="0xabcd")
        # macid (lowercase) should still be recognized as MacID
        assert "macid" in xml  # Tag preserves original case

    def test_integer_endtime_conversion(self):
        """Test that integer endtime values are converted to hex."""
        xml = generate_command_xml(None, Name="test", EndTime=3600)
        assert "<EndTime>0xe10</EndTime>" in xml

    def test_text_field(self):
        """Test text field passes through."""
        xml = generate_command_xml(None, Name="test", Text="Hello World")
        assert "<Text>Hello World</Text>" in xml

    def test_priority_field(self):
        """Test priority field."""
        xml = generate_command_xml(None, Name="test", Priority=1)
        assert "<Priority>1</Priority>" in xml

    def test_xml_formatting(self):
        """Test that XML is properly formatted."""
        xml = generate_command_xml(None, Name="test")
        # Should have XML declaration
        assert "<?xml" in xml
        # Should have LocalCommand root element
        assert "<LocalCommand>" in xml
        assert "</LocalCommand>" in xml
        # Should be indented (pretty printed)
        assert "  " in xml  # Contains indentation
