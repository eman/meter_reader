import requests
import logging
from typing import Any, Dict
from xml.sax.saxutils import escape

logger = logging.getLogger(__name__)


class EagleConfigClient:
    """Client for EAGLE Gateway system configuration via HTTP API (/cgi-bin/post_manager).
    
    This client provides access to system-level configuration endpoints including:
    - mDNS configuration and status
    - Remote management settings
    - Cloud service integration
    - Device configuration parameters
    """

    def __init__(self, address: str, username: str, password: str, timeout: int = 10) -> None:
        """Initialize the configuration client.
        
        Args:
            address: Gateway IP address or hostname
            username: HTTP Basic Auth username
            password: HTTP Basic Auth password
            timeout: Request timeout in seconds (default: 10)
        """
        self.base_url = f"http://{address}/cgi-bin/post_manager"
        self.auth = (username, password)
        self.timeout = timeout

    def _post_command(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Send a configuration command to post_manager endpoint.
        
        Args:
            name: Command name
            **kwargs: Additional command parameters
            
        Returns:
            Parsed JSON response from gateway
            
        Raises:
            requests.RequestException: If the HTTP request fails
        """
        # Build XML command with proper escaping to prevent XML injection
        xml_parts = ['<Command>']
        xml_parts.append(f'  <Name>{escape(name)}</Name>')
        xml_parts.append('  <Format>JSON</Format>')
        
        for key, value in kwargs.items():
            if value is not None:
                # Validate tag names are alphanumeric (allowlist approach)
                if not key.replace('_', '').isalnum():
                    logger.warning(f"Skipping parameter with invalid tag name: {key}")
                    continue
                escaped_value = escape(str(value))
                xml_parts.append(f'  <{key}>{escaped_value}</{key}>')
        
        xml_parts.append('</Command>')
        xml_payload = '\n'.join(xml_parts)
        
        try:
            resp = requests.post(
                self.base_url,
                data=xml_payload,
                auth=self.auth,
                timeout=self.timeout,
                headers={'Content-Type': 'text/xml'}
            )
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]
        except requests.RequestException as e:
            logger.error(f"Configuration request failed: {e}")
            raise

    def get_mdns_status(self) -> Dict[str, Any]:
        """Get mDNS (Multicast DNS) status and configuration.
        
        mDNS allows the gateway to be discovered on the local network using
        hostname instead of IP address (e.g., eagle-XXXXXX.local).
        
        Returns:
            Dictionary containing mDNS status information:
            - Enabled: "Y" or "N"
            - Hostname: mDNS hostname if enabled
            - Status: Current mDNS service status
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> status = client.get_mdns_status()
            >>> print(f"mDNS Enabled: {status.get('mDnsStatus', {}).get('Enabled')}")
        """
        return self._post_command('get_mdns_status')

    def set_mdns(self, enabled: bool) -> Dict[str, Any]:
        """Enable or disable mDNS service.
        
        Args:
            enabled: True to enable mDNS, False to disable
            
        Returns:
            Response from gateway confirming the change
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> response = client.set_mdns(enabled=True)
        """
        value = "Y" if enabled else "N"
        return self._post_command('set_mdns', Enabled=value)

    def get_device_config(self) -> Dict[str, Any]:
        """Get device configuration and status information.
        
        Returns information about the gateway device itself including:
        - Firmware version
        - Hardware version
        - MAC address
        - Update status
        - SSH access status
        - Cloud connectivity
        
        Returns:
            Dictionary containing device configuration details
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> config = client.get_device_config()
            >>> print(f"Firmware: {config.get('FirmwareVersion')}")
        """
        return self._post_command('get_device_config')

    def get_cloud_status(self) -> Dict[str, Any]:
        """Get cloud service connectivity and configuration status.
        
        Returns information about cloud service integration including:
        - Cloud provider (Rainforest, etc.)
        - Connection status
        - Account information
        - Push notification configuration
        
        Returns:
            Dictionary containing cloud status information
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> cloud = client.get_cloud_status()
            >>> print(f"Connected: {cloud.get('CloudStatus', {}).get('Connected')}")
        """
        return self._post_command('get_cloud_status')

    def get_remote_management_status(self) -> Dict[str, Any]:
        """Get remote management (Rainforest Remote) status and settings.
        
        Remote management allows secure off-site access to the gateway for
        monitoring and configuration via Rainforest's cloud service.
        
        Returns:
            Dictionary containing remote management status:
            - Enabled: Whether remote management is enabled
            - Status: Current connection status
            - Provider: Service provider (e.g., Rainforest)
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> remote = client.get_remote_management_status()
            >>> print(f"Remote enabled: {remote.get('RemoteEnabled')}")
        """
        return self._post_command('get_remote_management_status')

    def set_remote_management(self, enabled: bool) -> Dict[str, Any]:
        """Enable or disable remote management service.
        
        Args:
            enabled: True to enable remote management, False to disable
            
        Returns:
            Response from gateway confirming the change
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> response = client.set_remote_management(enabled=True)
        """
        value = "Y" if enabled else "N"
        return self._post_command('set_remote_management', Enabled=value)

    def get_ssh_status(self) -> Dict[str, Any]:
        """Get SSH (Secure Shell) access status.
        
        SSH access allows command-line access to the gateway for advanced
        configuration and troubleshooting (if enabled by the manufacturer).
        
        Returns:
            Dictionary containing SSH status information
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> ssh = client.get_ssh_status()
        """
        return self._post_command('get_ssh_status')

    def get_time_status(self) -> Dict[str, Any]:
        """Get gateway time and NTP (Network Time Protocol) status.
        
        Returns:
            Dictionary containing:
            - CurrentTime: Current time on gateway
            - NtpStatus: NTP synchronization status
            - TimeZone: Configured time zone
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> time_info = client.get_time_status()
            >>> print(f"Time: {time_info.get('CurrentTime')}")
        """
        return self._post_command('get_time_status')

    def get_network_info(self) -> Dict[str, Any]:
        """Get gateway network configuration.
        
        Returns:
            Dictionary containing network settings:
            - IPAddress: Current IP address
            - Netmask: Subnet mask
            - Gateway: Default gateway
            - DNS: DNS server addresses
            - DHCP: Whether DHCP is enabled
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> net = client.get_network_info()
            >>> print(f"IP: {net.get('IPAddress')}")
        """
        return self._post_command('get_network_info')

    def run_command(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Send an arbitrary configuration command.
        
        This is the underlying method used by all specific commands. Use this
        for commands not yet explicitly supported by the client.
        
        Args:
            name: Command name
            **kwargs: Command parameters
            
        Returns:
            Parsed JSON response from gateway
            
        Example:
            >>> client = EagleConfigClient("192.168.1.100", "admin", "password")
            >>> response = client.run_command('get_mdns_status')
        """
        return self._post_command(name, **kwargs)
