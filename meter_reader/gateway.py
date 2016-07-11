"""
Meter Reader

Copyright (c) 2016, Emmanuel Levijarvi
License: BSD 2-Clause
"""

import socket
from datetime import timedelta, datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
from contextlib import closing
import collections
# python 2/3 compatibilty fix-up
try:
    import StringIO
except ImportError:
    import io as StringIO

from meter_reader import utc

utctz = utc.UTC()
BEGINNING_OF_TIME = datetime(2000, 1, 1, tzinfo=utctz)

DEFAULT_PORT = 5002
COMMANDS = ('list_devices', 'get_device_data', 'get_instantaneous_demand',
            'get_demand_values', 'get_summation_values',
            'get_fast_poll_status')
SUPPORTED_ARGS = ('interval', 'frequency', 'starttime', 'endtime', 'duration',
                  'name')


class GatewayError(Exception):
    def __init__(self, address, command, error='', code=None):
        self.address = address
        self.code = code
        self.error = error
        self.command = command

    def __str__(self):
        return 'Unable to connect to {0}:{1}. {2}'.format(self.address[0],
                                                          self.address[1],
                                                          self.error)


class Gateway(object):
    def __init__(self, address, port=DEFAULT_PORT):
        self.address = (address, port)
        self.timeout = socket.getdefaulttimeout()
        self.mac_id = None
        devices = self.run_command(Name='list_devices', convert=False)
        self.mac_id = devices['DeviceInfo']['DeviceMacId']

    def generate_command_xml(self, **kwargs):
        c = ET.Element('LocalCommand')
        for tag, value in kwargs.items():
            if tag.lower() not in SUPPORTED_ARGS or value is None:
                continue
            if tag.lower() in ('starttime', 'endtime'):
                value = hex((value - BEGINNING_OF_TIME).seconds)
            elif tag.lower() in ('frequency', 'duration'):
                value = hex(value)
            ET.SubElement(c, tag).text = value
        if self.mac_id is not None:
            ET.SubElement(c, 'MacID').text = self.mac_id
        md = minidom.parseString(ET.tostring(c, encoding='utf-8'))
        return md.toprettyxml(indent="  ")

    def run_command_raw(self, **kwargs):
        with closing(socket.create_connection(self.address,
                                              self.timeout)) as s:
            s.sendall(self.generate_command_xml(**kwargs).encode('utf-8'))
            cmd_output = s.makefile().read()
        return cmd_output

    def run_command(self, convert=True, **kwargs):
        try:
            response = self.run_command_raw(**kwargs)
        except socket.error as e:
            raise GatewayError(self.address, kwargs.get('Name', ''),
                               e.strerror, e.errno)
        # responses come as multiple XML fragments. Enclose them in
        # <response> to ensure valid XML.
        if 'Interval data start' in response or 'HistoryData' in response:
            return self.xml2list('<response>{0}</response>'.format(response),
                                 convert)
        else:
            return self.xml2dict('<response>{0}</response>'.format(response),
                                 convert)

    @staticmethod
    def xml2dict(xml, convert=True):
        with closing(StringIO.StringIO(xml)) as f:
            path = [{}]
            for event, element in ET.iterparse(f, events=('start', 'end')):
                if element.tag == 'response':
                    continue
                if event == 'start':
                    if element.text is None or element.text.strip() != '':
                        if convert:
                            value = convert_data(element.tag, element.text)
                        else:
                            value = element.text
                        key = next(reversed(path[-1]))
                        path[-1][key][element.tag] = value
                    else:
                        new_level = collections.OrderedDict()
                        new_level[element.tag] = collections.OrderedDict()
                        path.append(new_level)
                elif element.text is not None and element.text.strip() == '':
                    later = path.pop()
                    path[-1].update(later)
        return path[0]

    @staticmethod
    def xml2list(xml, convert=True):
        with closing(StringIO.StringIO(xml)) as f:
            response = []
            for event, element in ET.iterparse(f, events=('start', 'end')):
                if element.tag in ('Info', 'Text', 'response'):
                    continue
                if event == 'start' and (element.text is not None and
                                         element.text.strip() == ''):
                    response.append({})
                if event == 'end' and (element.text is None or
                                       element.text.strip() != ''):
                    if convert:
                        value = convert_data(element.tag, element.text)
                    else:
                        value = element.text
                    response[-1][element.tag] = value
        return response

    def get_instantaneous_demand(self):
        resp = self.run_command(name='get_device_data')['InstantaneousDemand']
        demand = float(resp['Demand']) * resp['Multiplier'] / resp['Divisor']
        return (resp['TimeStamp'], demand)


def convert_data(key, value):
    if value is None:
        return
    if 'MacId' in key or 'Code' in key or 'Key' in key:
        len_ = 15
        if key == 'MeterMacId' or key == 'CoordMacId':
            len_ = 13
        return ':'.join(value.lstrip('0x')[i:i+2] for i in range(0, len_, 2))
    if key.lower() in ('timestamp', 'endtime') and int(value, 0):
        return BEGINNING_OF_TIME + timedelta(0, int(value, 0))
    if isinstance(value, str) and value.startswith('0x'):
        return int(value, 0)
    return value
