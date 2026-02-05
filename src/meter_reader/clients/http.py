import requests
import logging
from typing import Any, Dict

from .base import EagleClient
from ..models import (
    InstantaneousDemand, UsageData, DeviceList, NetworkInfo, 
    CurrentSummation, DeviceInfo
)
from ..utils import generate_command_xml

logger = logging.getLogger(__name__)

class EagleHttpClient(EagleClient):
    """Client for Eagle Energy Gateway via HTTP API (Port 80)."""

    def __init__(self, address: str, username: str, password: str, timeout: int = 10) -> None:
        self.base_url = f"http://{address}/cgi-bin/cgi_manager"
        self.auth = (username, password)
        self.timeout = timeout
        self.mac_id: str | None = None
        
        try:
            # Auto-detect MacID using get_device_list
            self.list_devices()
        except Exception:  # noqa: BLE001
            pass

    def _post_xml(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        xml_payload = generate_command_xml(self.mac_id, Name=name, **kwargs)
        try:
            resp = requests.post(
                self.base_url, 
                data=xml_payload, 
                auth=self.auth, 
                timeout=self.timeout
            )
            resp.raise_for_status()
            # The API returns JSON even though request is XML
            return resp.json()  # type: ignore[no-any-return]
        except requests.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            raise

    def list_devices(self) -> DeviceList:
        data = self._post_xml('get_device_list')
        
        # The JSON structure for device list is flat:
        # {
        #   "device_mac_id[0]": "...",
        #   "device_model_id[0]": "...",
        #   "num_devices": "1"
        # }
        # We need to transform this to the expected DeviceInfo list structure
        devices = []
        num_devices = int(data.get('num_devices', 0))
        
        for i in range(num_devices):
            mac_key = f'device_mac_id[{i}]'
            model_key = f'device_model_id[{i}]'
            if mac_key in data:
                devices.append(DeviceInfo(
                    DeviceMacId=data[mac_key],
                    ModelId=data.get(model_key),
                    # Other fields not available in this simple list
                ))
        
        if devices:
            self.mac_id = devices[0].device_mac_id
            
        return DeviceList(DeviceInfo=devices)

    def get_usage_data(self) -> UsageData:
        # HTTP API call: get_usage_data
        # This returns flat JSON with demand, summation, etc.
        data = self._post_xml('get_usage_data')
        return UsageData(**data)

    def get_instantaneous_demand(self) -> InstantaneousDemand:
        # Synthesize from usage data since HTTP endpoint is rich
        usage = self.get_usage_data()
        
        return InstantaneousDemand(
            DeviceMacId=self.mac_id or "unknown",
            MeterMacId="unknown", # Not always provided in JSON
            TimeStamp=usage.timestamp,
            Demand=usage.demand,
            Multiplier=1, # JSON is already normalized float
            Divisor=1,
            DigitsRight=0,
            DigitsLeft=0,
            SuppressLeadingZero=False
        )

    def get_current_summation(self) -> CurrentSummation:
        usage = self.get_usage_data()
        
        return CurrentSummation(
            DeviceMacId=self.mac_id or "unknown",
            MeterMacId="unknown",
            TimeStamp=usage.timestamp,
            SummationDelivered=int(usage.summation_delivered * 1000), # Back to int?
            SummationReceived=int(usage.summation_received * 1000),
            Multiplier=1, 
            Divisor=1000, # To match float value
            DigitsRight=3,
            DigitsLeft=0,
            SuppressLeadingZero=False
        )

    def get_network_info(self) -> NetworkInfo:
        # HTTP equivalent: get_device_config partial or not supported fully?
        # Post manager get_mdns_status exists.
        # cgi_manager returns some status.
        # Fallback for now: raise NotImplemented or return dummy
        # Based on probe: get_device_config returned update status, ssh enabled.
        # Network info (link strength) might not be exposed via HTTP easily.
        raise NotImplementedError("Network Info not fully supported via HTTP API yet.")
