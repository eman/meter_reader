"""Tests for meter_reader models module."""
import pytest
from datetime import datetime, timezone
from meter_reader.models import (
    InstantaneousDemand,
    CurrentSummation,
    UsageData,
    DeviceInfo,
    DeviceList,
    NetworkInfo,
)


class TestInstantaneousDemand:
    """Test InstantaneousDemand model."""

    def test_panic_demand_calculation(self):
        """Test panic_demand property calculates correctly."""
        demand = InstantaneousDemand(
            DeviceMacId="0xd8d5b9000000abcd",
            MeterMacId="0xd8d5b9000000abcd",
            TimeStamp=datetime.now(timezone.utc),
            Demand=1000,
            Multiplier=1,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=0,
            SuppressLeadingZero=False,
        )
        assert demand.panic_demand == 1.0

    def test_panic_demand_with_multiplier(self):
        """Test panic_demand with non-unity multiplier."""
        demand = InstantaneousDemand(
            DeviceMacId="0xd8d5b9000000abcd",
            MeterMacId="0xd8d5b9000000abcd",
            TimeStamp=datetime.now(timezone.utc),
            Demand=2500,
            Multiplier=2,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=0,
            SuppressLeadingZero=False,
        )
        assert demand.panic_demand == 5.0

    def test_field_aliases(self):
        """Test that field aliases work correctly."""
        data = {
            "DeviceMacId": "0xd8d5b9000000abcd",
            "MeterMacId": "0xd8d5b9000000abcd",
            "TimeStamp": datetime.now(timezone.utc),
            "Demand": 1000,
            "Multiplier": 1,
            "Divisor": 1000,
            "DigitsRight": 3,
            "DigitsLeft": 0,
            "SuppressLeadingZero": False,
        }
        demand = InstantaneousDemand(**data)
        assert demand.device_mac_id == data["DeviceMacId"]
        assert demand.meter_mac_id == data["MeterMacId"]


class TestCurrentSummation:
    """Test CurrentSummation model."""

    def test_delivered_kwh_calculation(self):
        """Test delivered_kwh property."""
        summation = CurrentSummation(
            DeviceMacId="0xd8d5b9000000abcd",
            MeterMacId="0xd8d5b9000000abcd",
            TimeStamp=datetime.now(timezone.utc),
            SummationDelivered=123456,
            SummationReceived=0,
            Multiplier=1,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=0,
            SuppressLeadingZero=False,
        )
        assert summation.delivered_kwh == 123.456

    def test_received_kwh_calculation(self):
        """Test received_kwh property."""
        summation = CurrentSummation(
            DeviceMacId="0xd8d5b9000000abcd",
            MeterMacId="0xd8d5b9000000abcd",
            TimeStamp=datetime.now(timezone.utc),
            SummationDelivered=0,
            SummationReceived=54321,
            Multiplier=1,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=0,
            SuppressLeadingZero=False,
        )
        assert summation.received_kwh == 54.321

    def test_both_kwh_calculations(self):
        """Test both delivered and received calculations."""
        summation = CurrentSummation(
            DeviceMacId="0xd8d5b9000000abcd",
            MeterMacId="0xd8d5b9000000abcd",
            TimeStamp=datetime.now(timezone.utc),
            SummationDelivered=100000,
            SummationReceived=50000,
            Multiplier=2,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=0,
            SuppressLeadingZero=False,
        )
        assert summation.delivered_kwh == 200.0
        assert summation.received_kwh == 100.0


class TestUsageData:
    """Test UsageData model."""

    def test_timestamp_property(self):
        """Test timestamp property converts unix timestamp."""
        usage = UsageData(
            demand=2.5,
            demand_units="kW",
            demand_timestamp=1609459200,  # 2021-01-01 00:00:00 UTC
            summation_delivered=100.5,
            summation_received=10.0,
            summation_units="kWh",
            meter_status="Connected",
        )
        expected = datetime.fromtimestamp(1609459200)
        assert usage.timestamp == expected

    def test_optional_consumption_field(self):
        """Test optional consumption field."""
        usage = UsageData(
            demand=2.5,
            demand_units="kW",
            demand_timestamp=1609459200,
            summation_delivered=100.5,
            summation_received=10.0,
            summation_units="kWh",
            meter_status="Connected",
            consumption=5.0,
        )
        assert usage.consumption == 5.0


class TestDeviceInfo:
    """Test DeviceInfo model."""

    def test_minimal_device_info(self):
        """Test DeviceInfo with minimal required fields."""
        device = DeviceInfo(DeviceMacId="0xd8d5b9000000abcd")
        assert device.device_mac_id == "0xd8d5b9000000abcd"
        assert device.model_id is None
        assert device.manufacturer is None

    def test_full_device_info(self):
        """Test DeviceInfo with all fields."""
        device = DeviceInfo(
            DeviceMacId="0xd8d5b9000000abcd",
            InstallCode="install123",
            LinkKey="key123",
            FWVersion="1.0.0",
            HWVersion="2.0.0",
            ImageType="0x1234",
            Manufacturer="TestMfg",
            ModelId="TEST-MODEL",
            DateCode="20210101",
        )
        assert device.device_mac_id == "0xd8d5b9000000abcd"
        assert device.fw_version == "1.0.0"
        assert device.manufacturer == "TestMfg"


class TestDeviceList:
    """Test DeviceList model."""

    def test_empty_device_list(self):
        """Test empty DeviceList."""
        devices = DeviceList()
        assert devices.device_info == []

    def test_device_list_with_devices(self):
        """Test DeviceList with multiple devices."""
        devices = DeviceList(
            DeviceInfo=[
                {"DeviceMacId": "0xd8d5b9000000abcd", "ModelId": "Model1"},
                {"DeviceMacId": "0xd8d5b9000000abce", "ModelId": "Model2"},
            ]
        )
        assert len(devices.device_info) == 2
        assert devices.device_info[0].model_id == "Model1"
        assert devices.device_info[1].model_id == "Model2"


class TestNetworkInfo:
    """Test NetworkInfo model."""

    def test_network_info(self):
        """Test NetworkInfo model with all fields."""
        network = NetworkInfo(
            DeviceMacId="0xd8d5b9000000abcd",
            CoordMacId="0xd8d5b9000000",
            Status="Connected",
            Description="Zigbee Network",
            ExtPanId="0x1234567890ABCDEF",
            Channel=15,
            ShortAddr="0x1234",
            LinkStrength=100,
        )
        assert network.device_mac_id == "0xd8d5b9000000abcd"
        assert network.status == "Connected"
        assert network.channel == 15
        assert network.link_strength == 100
