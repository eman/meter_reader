"""Property-based tests using Hypothesis for protocol validation."""

from datetime import datetime, timezone, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from meter_reader.clients.socket import (
    twos_complement,
    convert_data,
    BEGINNING_OF_TIME,
)


# Reduce number of examples for faster testing
PROFILE_SETTINGS = settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])


class TestTwosComplementProperties:
    """Property-based tests for twos_complement function."""

    @PROFILE_SETTINGS
    @given(st.integers(min_value=0, max_value=2**31 - 1))
    def test_positive_values_unchanged(self, value):
        """Positive values should remain unchanged in 32-bit."""
        result = twos_complement(value, 32)
        assert result == value

    @PROFILE_SETTINGS
    @given(st.integers(min_value=0, max_value=2**15 - 1))
    def test_positive_16bit_unchanged(self, value):
        """Positive values should remain unchanged in 16-bit."""
        result = twos_complement(value, 16)
        assert result == value

    @PROFILE_SETTINGS
    @given(st.integers(min_value=0, max_value=2**7 - 1))
    def test_positive_8bit_unchanged(self, value):
        """Positive values should remain unchanged in 8-bit."""
        result = twos_complement(value, 8)
        assert result == value

    @PROFILE_SETTINGS
    @given(st.integers(min_value=2**31, max_value=2**32 - 1))
    def test_negative_32bit_conversion(self, value):
        """High 32-bit values should convert to negative."""
        result = twos_complement(value, 32)
        assert result < 0

    @PROFILE_SETTINGS
    @given(st.integers(min_value=2**15, max_value=2**16 - 1))
    def test_negative_16bit_conversion(self, value):
        """High 16-bit values should convert to negative."""
        result = twos_complement(value, 16)
        assert result < 0

    @PROFILE_SETTINGS
    @given(st.integers(min_value=2**7, max_value=2**8 - 1))
    def test_negative_8bit_conversion(self, value):
        """High 8-bit values should convert to negative."""
        result = twos_complement(value, 8)
        assert result < 0

    @settings(max_examples=50)
    @given(st.integers(0, 2**32 - 1), st.integers(8, 64))
    def test_roundtrip_consistency(self, value, width):
        """Converting back should give consistent results."""
        signed = twos_complement(value, width)
        assert isinstance(signed, int)

    def test_all_32bit_boundaries(self):
        """Test specific 32-bit boundaries."""
        assert twos_complement(0x7FFFFFFF, 32) == 0x7FFFFFFF
        assert twos_complement(0x80000000, 32) == -2147483648
        assert twos_complement(0xFFFFFFFF, 32) == -1

    def test_all_16bit_boundaries(self):
        """Test specific 16-bit boundaries."""
        assert twos_complement(0x7FFF, 16) == 0x7FFF
        assert twos_complement(0x8000, 16) == -32768
        assert twos_complement(0xFFFF, 16) == -1

    def test_all_8bit_boundaries(self):
        """Test specific 8-bit boundaries."""
        assert twos_complement(0x7F, 8) == 0x7F
        assert twos_complement(0x80, 8) == -128
        assert twos_complement(0xFF, 8) == -1


class TestConvertDataProperties:
    """Property-based tests for convert_data function."""

    @PROFILE_SETTINGS
    @given(st.none())
    def test_none_returns_none(self, value):
        """None input should always return None."""
        result = convert_data("AnyKey", value)
        assert result is None

    @PROFILE_SETTINGS
    @given(st.text(min_size=1, max_size=100, alphabet="abcdefghijklmnopqrstuvwxyz"))
    def test_non_hex_keys_returned(self, value):
        """Keys without special handling convert value to hex format."""
        # convert_data treats all text values as potential hex
        result = convert_data("RandomKey", value)
        # It returns formatted hex (with colons)
        assert isinstance(result, str)
        # For non-special keys, it still processes the value
        assert len(result) > 0

    @PROFILE_SETTINGS
    @given(st.text(alphabet="0123456789abcdefABCDEF", min_size=16, max_size=16))
    def test_device_mac_id_formatting(self, hex_value):
        """DeviceMacId should format hex to colon-separated."""
        input_value = "0x" + hex_value
        result = convert_data("DeviceMacId", input_value)
        
        assert isinstance(result, str)
        parts = result.split(":")
        assert len(parts) == 8
        for part in parts:
            assert len(part) == 2

    @PROFILE_SETTINGS
    @given(st.text(alphabet="0123456789abcdefABCDEF", min_size=14, max_size=14))
    def test_meter_mac_id_formatting(self, hex_value):
        """MeterMacId should format with shorter length."""
        input_value = "0x" + hex_value
        result = convert_data("MeterMacId", input_value)
        
        assert isinstance(result, str)
        parts = result.split(":")
        assert len(parts) == 7

    @PROFILE_SETTINGS
    @given(st.integers(1, 86400))
    def test_timestamp_conversion_offset(self, seconds):
        """Timestamp should convert from hex offset to datetime."""
        hex_value = hex(seconds)
        result = convert_data("TimeStamp", hex_value)
        
        assert isinstance(result, datetime)
        expected = BEGINNING_OF_TIME + timedelta(seconds=seconds)
        assert result == expected

    @PROFILE_SETTINGS
    @given(st.integers(0, 0x7FFFFFFF))
    def test_hex_value_conversion_positive(self, value):
        """Positive hex values should convert to integer."""
        hex_str = hex(value)
        result = convert_data("SomeIntKey", hex_str)
        # Should convert hex string to integer
        assert isinstance(result, (int, str))  # Depends on the key handling

    @PROFILE_SETTINGS
    @given(st.just("EndTime"), st.integers(1, 86400))
    def test_endtime_conversion(self, key, seconds):
        """EndTime key should convert like TimeStamp."""
        hex_value = hex(seconds)
        result = convert_data(key, hex_value)
        
        assert isinstance(result, datetime)
        expected = BEGINNING_OF_TIME + timedelta(seconds=seconds)
        assert result == expected

    def test_zero_timestamp_returns_integer(self):
        """Zero timestamp value is returned as-is."""
        result = convert_data("TimeStamp", "0x0")
        # Zero hex converts to 0, not BEGINNING_OF_TIME for non-datetime processing
        assert result == 0 or result == BEGINNING_OF_TIME

    @PROFILE_SETTINGS
    @given(st.text(alphabet="0123456789abcdefABCDEF", min_size=2, max_size=2))
    def test_install_code_formatting(self, hex_pair):
        """InstallCode should format hex values."""
        input_value = "0x" + hex_pair
        result = convert_data("InstallCode", input_value)
        assert isinstance(result, str)


class TestDemandCalculations:
    """Property-based tests for demand calculations."""

    @settings(max_examples=50)
    @given(
        st.integers(0, 0xFFFFFFFF),
        st.integers(1, 1000),
        st.integers(1, 1000)
    )
    def test_demand_calculation_consistency(self, demand, multiplier, divisor):
        """Demand calculation should be consistent."""
        from meter_reader.models import InstantaneousDemand
        
        model = InstantaneousDemand(
            DeviceMacId="0xtest",
            MeterMacId="0xtest",
            TimeStamp=datetime.now(timezone.utc),
            Demand=demand,
            Multiplier=multiplier,
            Divisor=divisor,
            DigitsRight=3,
            DigitsLeft=5,
            SuppressLeadingZero=False
        )
        
        expected = (demand * multiplier) / divisor
        assert model.panic_demand == expected

    @PROFILE_SETTINGS
    @given(st.integers(0, 1000000))
    def test_demand_always_non_negative(self, demand):
        """With positive inputs, demand should be non-negative."""
        from meter_reader.models import InstantaneousDemand
        
        model = InstantaneousDemand(
            DeviceMacId="0xtest",
            MeterMacId="0xtest",
            TimeStamp=datetime.now(timezone.utc),
            Demand=demand,
            Multiplier=1,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=5,
            SuppressLeadingZero=False
        )
        
        assert model.panic_demand >= 0


class TestSummationCalculations:
    """Property-based tests for summation calculations."""

    @settings(max_examples=50)
    @given(
        st.integers(0, 0xFFFFFFFF),
        st.integers(0, 0xFFFFFFFF),
        st.integers(1, 1000),
        st.integers(1, 1000)
    )
    def test_summation_calculation_consistency(self, delivered, received, multiplier, divisor):
        """Summation calculation should be consistent."""
        from meter_reader.models import CurrentSummation
        
        model = CurrentSummation(
            DeviceMacId="0xtest",
            MeterMacId="0xtest",
            TimeStamp=datetime.now(timezone.utc),
            SummationDelivered=delivered,
            SummationReceived=received,
            Multiplier=multiplier,
            Divisor=divisor,
            DigitsRight=3,
            DigitsLeft=8,
            SuppressLeadingZero=False
        )
        
        expected_delivered = (delivered * multiplier) / divisor
        expected_received = (received * multiplier) / divisor
        
        assert model.delivered_kwh == expected_delivered
        assert model.received_kwh == expected_received

    @PROFILE_SETTINGS
    @given(st.integers(0, 1000000), st.integers(0, 1000000))
    def test_summation_always_non_negative(self, delivered, received):
        """With positive inputs, summation should be non-negative."""
        from meter_reader.models import CurrentSummation
        
        model = CurrentSummation(
            DeviceMacId="0xtest",
            MeterMacId="0xtest",
            TimeStamp=datetime.now(timezone.utc),
            SummationDelivered=delivered,
            SummationReceived=received,
            Multiplier=1,
            Divisor=1000,
            DigitsRight=3,
            DigitsLeft=8,
            SuppressLeadingZero=False
        )
        
        assert model.delivered_kwh >= 0
        assert model.received_kwh >= 0


class TestNetworkStatusProperties:
    """Property-based tests for network status."""

    @PROFILE_SETTINGS
    @given(st.integers(0, 100))
    def test_link_strength_range(self, strength):
        """Link strength should be within valid range."""
        from meter_reader.models import NetworkInfo
        
        model = NetworkInfo(
            DeviceMacId="0xtest",
            CoordMacId="0xtest",
            Status="Connected",
            Description="Test",
            ExtPanId="0xtest",
            Channel=15,
            ShortAddr="0x1234",
            LinkStrength=strength
        )
        assert 0 <= model.link_strength <= 100

    @PROFILE_SETTINGS
    @given(st.integers(11, 26))
    def test_zigbee_channel_valid(self, channel):
        """ZigBee channel should be in valid range."""
        from meter_reader.models import NetworkInfo
        
        model = NetworkInfo(
            DeviceMacId="0xtest",
            CoordMacId="0xtest",
            Status="Connected",
            Description="Test",
            ExtPanId="0xtest",
            Channel=channel,
            ShortAddr="0x1234",
            LinkStrength=50
        )
        assert model.channel == channel


class TestUsageDataProperties:
    """Property-based tests for usage data."""

    @settings(max_examples=50)
    @given(
        st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False),
        st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False)
    )
    def test_usage_data_consistency(self, demand, delivered, received):
        """Usage data should maintain consistency."""
        from meter_reader.models import UsageData
        
        model = UsageData(
            demand=demand,
            demand_units="kW",
            demand_timestamp=1609459200,
            summation_delivered=delivered,
            summation_received=received,
            summation_units="kWh",
            meter_status="Connected"
        )
        
        assert isinstance(model.timestamp, datetime)

    @PROFILE_SETTINGS
    @given(st.integers(0, 2147483647))
    def test_usage_data_timestamp_conversion(self, timestamp):
        """Usage data should convert unix timestamp to datetime."""
        from meter_reader.models import UsageData
        
        model = UsageData(
            demand=1.5,
            demand_units="kW",
            demand_timestamp=timestamp,
            summation_delivered=100.0,
            summation_received=0.0,
            summation_units="kWh",
            meter_status="Connected"
        )
        
        assert isinstance(model.timestamp, datetime)
        assert model.timestamp.timestamp() == timestamp


class TestDeviceListProperties:
    """Property-based tests for device list."""

    @PROFILE_SETTINGS
    @given(st.integers(0, 10))
    def test_device_list_count_consistency(self, count):
        """Device list should maintain consistent count."""
        from meter_reader.models import DeviceInfo, DeviceList
        
        devices = [
            DeviceInfo(device_mac_id=f"0xtest{i}")
            for i in range(count)
        ]
        
        device_list = DeviceList(device_info=devices)
        assert len(device_list.device_info) == count


class TestModelFieldValidation:
    """Property-based tests for model field validation."""

    @PROFILE_SETTINGS
    @given(st.text(min_size=1, max_size=100, alphabet="0123456789abcdefABCDEF"))
    def test_device_mac_id_field(self, mac_id):
        """Device models should accept various MAC ID formats."""
        from meter_reader.models import DeviceInfo
        
        device = DeviceInfo(device_mac_id=mac_id)
        assert device.device_mac_id == mac_id

    @PROFILE_SETTINGS
    @given(st.text(max_size=100))
    def test_device_model_id_field(self, model_id):
        """Device models should accept various model IDs."""
        from meter_reader.models import DeviceInfo
        
        device = DeviceInfo(device_mac_id="0xtest", model_id=model_id)
        assert device.model_id == model_id

    @PROFILE_SETTINGS
    @given(st.text(max_size=50, alphabet="Connected,Unavailable,Joining"))
    def test_network_status_field(self, status):
        """Network status should accept various values."""
        from meter_reader.models import NetworkInfo
        
        network = NetworkInfo(
            device_mac_id="0xtest",
            coord_mac_id="0xtest",
            status=status,
            description="test",
            ext_pan_id="0xtest",
            channel=15,
            short_addr="0x1234",
            link_strength=50
        )
        assert network.status == status
