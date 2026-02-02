import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from typing import Any

from .clients.base import EagleClient # Circular import risk? No, utils is imported by clients.
# Wait, avoiding circular dependency. 
# Constants
BEGINNING_OF_TIME = datetime(2000, 1, 1)

SUPPORTED_ARGS = ('interval', 'frequency', 'starttime', 'endtime', 'duration',
                  'name', 'event', 'enabled', 'protocol', 'macid',
                  'devicemacid', 'metermacid', 'target', 'format', 'priority',
                  'text', 'confirmationrequired', 'id', 'queue', 'read')

def generate_command_xml(mac_id: str | None, **kwargs: Any) -> str:
    c = ET.Element('LocalCommand')
    has_mac_arg = any(k.lower() in ('macid', 'devicemacid', 'metermacid') for k in kwargs)
    
    for tag, value in kwargs.items():
        if tag.lower() not in SUPPORTED_ARGS or value is None:
            continue
        if tag.lower() in ('starttime', 'endtime'):
             if isinstance(value, datetime):
                 # datetime arithmetic
                 diff = (value.replace(tzinfo=None) - BEGINNING_OF_TIME).total_seconds()
                 value = hex(int(diff))
             elif isinstance(value, int):
                 value = hex(value)
        elif tag.lower() in ('frequency', 'duration'):
            value = hex(value)
        
        ET.SubElement(c, tag).text = str(value)
        
    if not has_mac_arg and mac_id is not None:
        ET.SubElement(c, 'MacID').text = mac_id
        
    md = minidom.parseString(ET.tostring(c, encoding='utf-8'))
    return md.toprettyxml(indent="  ")
