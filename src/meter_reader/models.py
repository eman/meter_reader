from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class EagleModel(BaseModel):
    """Base model for Eagle Gateway responses."""
    model_config = ConfigDict(populate_by_name=True)

class DeviceInfo(EagleModel):
    device_mac_id: str = Field(alias='DeviceMacId')
    install_code: Optional[str] = Field(default=None, alias='InstallCode')
    link_key: Optional[str] = Field(default=None, alias='LinkKey')
    fw_version: Optional[str] = Field(default=None, alias='FWVersion')
    hw_version: Optional[str] = Field(default=None, alias='HWVersion')
    image_type: Optional[str | int] = Field(default=None, alias='ImageType')
    manufacturer: Optional[str] = Field(default=None, alias='Manufacturer')
    model_id: Optional[str] = Field(default=None, alias='ModelId')
    date_code: Optional[str] = Field(default=None, alias='DateCode')

class DeviceList(EagleModel):
    device_info: List[DeviceInfo] = Field(default_factory=list, alias='DeviceInfo')

class InstantaneousDemand(EagleModel):
    device_mac_id: str = Field(alias='DeviceMacId')
    meter_mac_id: str = Field(alias='MeterMacId')
    timestamp: datetime = Field(alias='TimeStamp')
    demand: float = Field(alias='Demand')
    multiplier: float = Field(alias='Multiplier')
    divisor: float = Field(alias='Divisor')
    digits_right: int = Field(alias='DigitsRight')
    digits_left: int = Field(alias='DigitsLeft')
    suppress_leading_zero: bool = Field(alias='SuppressLeadingZero')

    @property
    def panic_demand(self) -> float:
         """Calculate demand in kW."""
         return (self.demand * self.multiplier) / self.divisor

class CurrentSummation(EagleModel):
    device_mac_id: str = Field(alias='DeviceMacId')
    meter_mac_id: str = Field(alias='MeterMacId')
    timestamp: datetime = Field(alias='TimeStamp')
    summation_delivered: int = Field(alias='SummationDelivered')
    summation_received: int = Field(alias='SummationReceived')
    multiplier: float = Field(alias='Multiplier')
    divisor: float = Field(alias='Divisor')
    digits_right: int = Field(alias='DigitsRight')
    digits_left: int = Field(alias='DigitsLeft')
    suppress_leading_zero: bool = Field(alias='SuppressLeadingZero')

    @property
    def delivered_kwh(self) -> float:
        return (self.summation_delivered * self.multiplier) / self.divisor

    @property
    def received_kwh(self) -> float:
        return (self.summation_received * self.multiplier) / self.divisor

class NetworkInfo(EagleModel):
    device_mac_id: str = Field(alias='DeviceMacId')
    coord_mac_id: str = Field(alias='CoordMacId')
    status: str = Field(alias='Status')
    description: str = Field(alias='Description')
    ext_pan_id: str = Field(alias='ExtPanId')
    channel: int = Field(alias='Channel')
    short_addr: str = Field(alias='ShortAddr')
    link_strength: int = Field(alias='LinkStrength')

class UsageData(EagleModel):
    """Model for HTTP endpoint response."""
    # HTTP endpoint fields are snake_case naturally in JSON
    demand: float
    demand_units: str
    demand_timestamp: int
    summation_received: float
    summation_delivered: float
    summation_units: str
    meter_status: str
    consumption: Optional[float] = None
    
    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.demand_timestamp)
