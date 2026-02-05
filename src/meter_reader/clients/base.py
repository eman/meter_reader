from abc import ABC, abstractmethod

from ..models import InstantaneousDemand, UsageData, DeviceList, NetworkInfo, CurrentSummation

class EagleClient(ABC):
    """Abstract base class for Eagle Gateway clients."""

    @abstractmethod
    def list_devices(self) -> DeviceList:
        """List devices connected to the gateway."""
        pass

    @abstractmethod
    def get_instantaneous_demand(self) -> InstantaneousDemand:
        """Get real-time demand data."""
        pass
    
    @abstractmethod
    def get_current_summation(self) -> CurrentSummation:
        """Get total consumption to date."""
        pass
    
    @abstractmethod
    def get_usage_data(self) -> UsageData:
        """Get usage data (demand + summation)."""
        pass
        
    @abstractmethod
    def get_network_info(self) -> NetworkInfo:
        """Get Zigbee network information."""
        pass
