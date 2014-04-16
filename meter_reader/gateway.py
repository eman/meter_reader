"""
Meter Reader

:copyright: (c) 2014 by Emmanuel Levijarvi
:license: BSD
"""

import sys
import socket
from datetime import timedelta, datetime
import xml.etree.ElementTree as ET
from contextlib import closing
# python 2/3 compatibilty fix-up
try:
    import StringIO
except ImportError:
    import io as StringIO

from meter_reader import utc

utctz = utc.UTC() 
BEGINNING_OF_TIME = datetime(2000, 1, 1, tzinfo=utctz)

DEFAULT_PORT = 5002
COMMANDS = ['LIST_DEVICES', 'GET_DEVICE_DATA', 'GET_INSTANTANEOUS_DEMAND',
            'GET_DEMAND_VALUES', 'GET_SUMMATION_VALUES',
            'GET_FAST_POLL_STATUS']

COMMAND_XML = '''
<LocalCommand>
    <Name>{0}</Name>
    <MacId>{1}</MacId>
</LocalCommand>
'''

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
        self.mac_id = '0xffffffffffffffff'
        devices = self.run_command('LIST_DEVICES', convert=False)
        self.mac_id = devices['DeviceInfo']['DeviceMacId']

    def run_command_raw(self, command):
        with closing(socket.create_connection(self.address, self.timeout)) as s:
            s.sendall(COMMAND_XML.format(command, self.mac_id).encode('utf-8'))
            cmd_output = s.makefile().read()
        return cmd_output

    def run_command(self, command, convert=True):
        try:
            response = self.run_command_raw(command)
        except socket.error as e:
            raise GatewayError(self.address, command, e.strerror, e.errno)
        # responses come as multiple XML fragments. Enclose them in
        # <response> to ensure valid XML.
        return self.xml2dict('<response>{0}</response>'.format(response),
                             convert)

    @staticmethod
    def xml2dict(xml, convert=True):
        with closing(StringIO.StringIO(xml)) as f:
            path = []
            response = {}
            for event, element in ET.iterparse(f, events=('start', 'end')):
                if element.tag == 'response':
                    continue
                if event == 'start':
                    path.append(element.tag)
                    if element.text is None or element.text.strip() != '':
                        if convert:
                            data = convert_data(element.tag, element.text)
                        else:
                            data = element.text
                        try:
                            response[path[0]][element.tag] = data
                        except KeyError:
                            response[path[0]] = {element.tag: data}
                else:
                    path.pop()
        return response

    @staticmethod
    def xml2dict2(xml):
        with closing(StringIO.StringIO(xml)) as f:
            path = []
            response = []
            for event, element in ET.iterparse(f, events=('start', 'end')):
                if element.tag == "response":
                    continue
                if event == 'start':
                    path.append(element.tag)
                else:
                    path.pop()

    def get_instantaneous_demand(self):
        resp = self.run_command('GET_DEVICE_DATA')['InstantaneousDemand']
        demand = float(resp['Demand']) * resp['Multiplier'] / resp['Divisor']
        return (resp['TimeStamp'], demand)


def convert_data(key, value):
    if value is None:
        return None
    if 'MacId' in key or 'Code' in key or 'Key' in key:
        len_ = 15
        if key == 'MeterMacId' or key == 'CoordMacId':
            len_ = 13
        return ':'.join(value.lstrip('0x')[i:i+2] for i in range(0, len_, 2))
    if key == 'TimeStamp':
        ts = (BEGINNING_OF_TIME + timedelta(0, int(value, 0)))
        return ts
    if isinstance(value, str) and value.startswith('0x'):
        return int(value, 0)
    return value
