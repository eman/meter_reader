"""
Meter Reader

A client library and command-line tool for retrieving smart meter data from
an Eagle Energy Gateway.

:copyright: (c) 2017-2026 by Emmanuel Levijarvi
:license: BSD 2-Clause
"""

from .clients import SocketClient as EagleSocketClient, HttpClient as EagleHttpClient, ConfigClient as EagleConfigClient
from .models import InstantaneousDemand, UsageData, CurrentSummation, NetworkInfo, DeviceList

__version__ = "2.0.0"
__author__ = "Emmanuel Levijarvi"
__all__ = [
    'EagleSocketClient', 'EagleHttpClient', 'EagleConfigClient',
    'InstantaneousDemand', 'UsageData', 
    'CurrentSummation', 'NetworkInfo', 'DeviceList'
]
