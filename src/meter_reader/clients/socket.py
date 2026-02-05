import socket
import logging
from contextlib import closing
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Tuple
import xml.etree.ElementTree as ET
from xml.dom import minidom

from ..models import (
    InstantaneousDemand,
    UsageData,
    DeviceList,
    NetworkInfo,
    CurrentSummation,
)
from .base import EagleClient

logger = logging.getLogger(__name__)

utctz = timezone.utc
BEGINNING_OF_TIME = datetime(2000, 1, 1, tzinfo=utctz)
DEFAULT_PORT = 5002
DEFAULT_TIMEOUT = 5
MAX_RESPONSE_SIZE = 1024 * 1024  # 1 MB max response

SUPPORTED_ARGS = (
    "interval",
    "frequency",
    "starttime",
    "endtime",
    "duration",
    "name",
    "event",
    "enabled",
    "protocol",
    "macid",
    "devicemacid",
    "metermacid",
    "target",
    "format",
    "priority",
    "text",
    "confirmationrequired",
    "id",
    "queue",
    "read",
)


class GatewayError(Exception):
    """Exception raised when gateway communication fails."""

    def __init__(
        self,
        address: Tuple[str, int],
        command: str,
        error: str = "",
        code: int | None = None,
    ) -> None:
        self.address = address
        self.code = code
        self.error = error
        self.command = command

    def __str__(self) -> str:
        return f"Unable to connect to {self.address[0]}:{self.address[1]}. {self.error}"


def twos_complement(value: int, width: int = 32) -> int:
    if value & (1 << (width - 1)):
        value = value - (1 << width)
    return value


def convert_data(key: str, value: str | None) -> Any:
    if value is None:
        return None
    if "MacId" in key or "Code" in key or "Key" in key:
        clean_value = value
        if value.lower().startswith("0x"):
            clean_value = value[2:]
        len_ = 15
        if key == "MeterMacId" or key == "CoordMacId":
            len_ = 13
        return ":".join(clean_value[i : i + 2] for i in range(0, len_, 2))
    if key.lower() in ("timestamp", "endtime") and int(value, 0):
        # Handle time offset from 2000-01-01
        return BEGINNING_OF_TIME + timedelta(0, int(value, 16))
    if isinstance(value, str) and value.startswith("0x"):
        return twos_complement(int(value, 16))
    return value


class EagleSocketClient(EagleClient):
    """Client for Eagle Energy Gateway via Socket API (Port 5002)."""

    def __init__(
        self, address: str, port: int = DEFAULT_PORT, timeout: int = DEFAULT_TIMEOUT
    ) -> None:
        self.address = (address, port)
        self.timeout = timeout
        self.mac_id: str | None = None

        # Initialize by fetching device list to get MAC ID
        try:
            self._fetch_device_list()
        except Exception as e:
            logger.warning(f"Failed to auto-discover MAC ID: {e}")

    def _fetch_device_list(self) -> None:
        data = self._run_command_dict(Name="list_devices", convert=False)
        # Handle case where DeviceInfo is a list or single dict
        if "DeviceInfo" in data:
            info = data["DeviceInfo"]
            if isinstance(info, list) and info:
                self.mac_id = info[0].get("DeviceMacId")
            elif isinstance(info, dict):
                self.mac_id = info.get("DeviceMacId")

    def generate_command_xml(self, **kwargs: Any) -> str:
        c = ET.Element("LocalCommand")
        has_mac_arg = any(
            k.lower() in ("macid", "devicemacid", "metermacid") for k in kwargs
        )

        for tag, value in kwargs.items():
            if tag.lower() not in SUPPORTED_ARGS or value is None:
                continue
            if tag.lower() in ("starttime", "endtime"):
                if isinstance(value, datetime):
                    value = hex(int((value - BEGINNING_OF_TIME).total_seconds()))
                elif isinstance(value, int):
                    value = hex(value)
            elif tag.lower() in ("frequency", "duration"):
                value = hex(value)

            ET.SubElement(c, tag).text = str(value)

        if not has_mac_arg and self.mac_id is not None:
            ET.SubElement(c, "MacID").text = self.mac_id

        md = minidom.parseString(ET.tostring(c, encoding="utf-8"))
        return md.toprettyxml(indent="  ")

    def _run_command_raw(self, **kwargs: Any) -> str:
        try:
            with closing(socket.create_connection(self.address, self.timeout)) as s:
                s.sendall(self.generate_command_xml(**kwargs).encode("utf-8"))
                response = b""
                s.settimeout(self.timeout)
                try:
                    while len(response) < MAX_RESPONSE_SIZE:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        response += chunk
                except socket.timeout:
                    pass
                if len(response) >= MAX_RESPONSE_SIZE:
                    logger.warning(
                        f"Response exceeded maximum size ({MAX_RESPONSE_SIZE} bytes) "
                        f"from {self.address}"
                    )
                return response.decode("utf-8", errors="replace")
        except socket.error as e:
            raise GatewayError(self.address, kwargs.get("Name", ""), str(e))

    def _element_to_data(self, element: ET.Element, convert: bool = True) -> Any:
        # 1. If element has no children, return text value
        if len(element) == 0:
            if convert:
                return convert_data(element.tag, element.text)
            return element.text

        # 2. Iterate children and build dict
        result: Dict[str, Any] = {}
        child_counts: Dict[str, int] = {}

        # First pass to count occurrences for list detection
        for child in element:
            child_counts[child.tag] = child_counts.get(child.tag, 0) + 1

        for child in element:
            tag = child.tag
            if tag in ("Info", "Text"):
                continue

            value = self._element_to_data(child, convert)

            # If tag appears multiple times, it must be a list
            if child_counts[tag] > 1:
                if tag not in result:
                    result[tag] = []
                result[tag].append(value)
            else:
                result[tag] = value

        # If result is empty (all children were skipped), return element text or None
        if not result:
            if convert:
                return convert_data(element.tag, element.text)
            return element.text

        return result

    def _xml2dict(self, xml: str, convert: bool = True) -> Dict[str, Any]:
        if not xml.strip():
            return {}
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            return {}

        if root.tag == "response":
            return self._element_to_data(root, convert)  # type: ignore
        else:
            return {root.tag: self._element_to_data(root, convert)}

    def _run_command_dict(self, convert: bool = True, **kwargs: Any) -> Dict[str, Any]:
        raw_xml = self._run_command_raw(**kwargs)
        # Check for list wrapper
        return self._xml2dict(f"<response>{raw_xml}</response>", convert)

    def list_devices(self) -> DeviceList:
        data = self._run_command_dict(Name="list_devices")
        # Ensure DeviceInfo is a list for the model, even if single device
        if "DeviceInfo" in data and not isinstance(data["DeviceInfo"], list):
            data["DeviceInfo"] = [data["DeviceInfo"]]
        return DeviceList(**data)

    def get_instantaneous_demand(self) -> InstantaneousDemand:
        # The command is 'get_instantaneous_demand' and requires DeviceMacId
        data = self._run_command_dict(
            Name="get_instantaneous_demand", DeviceMacId=self.mac_id
        )
        # Unwrap if needed, usually InstantaneousDemand key is at root
        if "InstantaneousDemand" in data:
            return InstantaneousDemand(**data["InstantaneousDemand"])
        return InstantaneousDemand(**data)

    def get_current_summation(self) -> CurrentSummation:
        # get_current_summation doesn't exist, use get_device_data which returns all data
        data = self._run_command_dict(Name="get_device_data", DeviceMacId=self.mac_id)
        if "CurrentSummation" in data:
            return CurrentSummation(**data["CurrentSummation"])
        raise ValueError("CurrentSummation not found in device data")

    def get_network_info(self) -> NetworkInfo:
        # Use get_device_data which includes NetworkInfo
        data = self._run_command_dict(Name="get_device_data", DeviceMacId=self.mac_id)
        if "NetworkInfo" in data:
            return NetworkInfo(**data["NetworkInfo"])
        raise ValueError("NetworkInfo not found in device data")

    def get_usage_data(self) -> UsageData:
        # Socket API doesn't have a direct equivalent to the HTTP usage_data summary
        # that includes both demand and summation in one flat object cleanly.
        # We can simulate it by fetching both.
        instant = self.get_instantaneous_demand()
        summation = self.get_current_summation()

        return UsageData(
            demand=instant.demand,  # Raw demand
            demand_units="kW",  # Implicit in socket model usually
            demand_timestamp=int(instant.timestamp.timestamp()),
            summation_delivered=summation.delivered_kwh,
            summation_received=summation.received_kwh,
            summation_units="kWh",
            meter_status="Connected",  # Assumed if we got data
        )

    def get_history_data(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        frequency: int = 0x384,
    ) -> List[CurrentSummation]:
        """
        Get historical summation data.

        Args:
            start_time: Start time for history query (defaults to 1 hour ago)
            end_time: End time for history query (defaults to now)
            frequency: Sample frequency in seconds (hex). 0x384 = 900 = 15 minutes

        Returns:
            List of CurrentSummation objects
        """
        if start_time is None:
            start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        if end_time is None:
            end_time = datetime.now(timezone.utc)

        data = self._run_command_dict(
            Name="get_history_data",
            DeviceMacId=self.mac_id,
            StartTime=start_time,
            EndTime=end_time,
            Frequency=frequency,
        )

        # History data returns a HistoryData wrapper with multiple CurrentSummation entries
        if "HistoryData" in data:
            history = data["HistoryData"]
            if "CurrentSummation" in history:
                summations = history["CurrentSummation"]
                # Ensure it's a list
                if not isinstance(summations, list):
                    summations = [summations]
                return [CurrentSummation(**s) for s in summations]

        return []
