"""
Meter Reader
------------------------------------------------------------------------------

Meter Reader is a command line client for retrieving data
from the Eagle Energy Gateway.

More information on the Eagle Engergy Gateway can be found here:
http://www.rainforestautomation.com

:copyright: (c) 2013 by Emmanuel Levijarvi
:license: BSD
"""

from __future__ import print_function
import sys
import socket
import argparse
import xml.etree.ElementTree as ET
from contextlib import closing
# python 2/3 compatibilty fix-up
try:
    import StringIO
except ImportError:
    import io as StringIO

DEFAULT_PORT = 5002
COMMANDS = ['LIST_DEVICES', 'GET_DEVICE_DATA', 'GET_INSTANTANEOUS_DEMAND',
            'GET_DEMAND_VALUES', 'GET_SUMMATION_VALUES']

COMMAND_XML = '''
<LocalCommand>
    <Name>{0}</Name>
    <MacId>{1}</MacId>
</LocalCommand>
'''


class Gateway(object):
    def __init__(self, address, port=DEFAULT_PORT):
        self.address = address
        self.port = port
        self.mac_id = '0xffffffffffffffff'
        devices = self.run_command('LIST_DEVICES')
        self.mac_id = devices['DeviceInfo']['DeviceMacId']

    def run_command_raw(self, command):
        with closing(socket.create_connection((self.address, self.port))) as s:
            s.sendall(COMMAND_XML.format(command, self.mac_id).encode())
            cmd_output = s.makefile().read()
        # responses come as multiple XML fragments. Enclose them in
        # <response> to ensure valid XML.
        return '<response>{0}</response>'.format(cmd_output)

    def run_command(self, command):
        return self.xml2dict(self.run_command_raw(command))

    @staticmethod
    def xml2dict(xml):
        with closing(StringIO.StringIO(xml)) as f:
            path = []
            response = {}
            for event, element in ET.iterparse(f, events=('start', 'end')):
                if element.tag == 'response':
                    continue
                if event == 'start':
                    path.append(element.tag)
                    if element.text is None or element.text.strip() != '':
                        try:
                            response[path[0]][element.tag] = element.text
                        except KeyError:
                            response[path[0]] = {element.tag: element.text}
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


def display(output):
    keywidth = 0
    for section in output:
        for key in output[section]:
            if len(key) > keywidth:
                keywidth = len(key)
    for section in output:
        print(section)
        for key, value in list(output[section].items()):
            if 'MacId' in key or 'Code' in key or 'Key' in key:
                value = ':'.join(value.lstrip('0x')[i:i+2]
                                 for i in range(0, 15, 2))
            elif value is not None and value.startswith('0x'):
                value = int(value, 0)
            print(' ' * 3, key.ljust(keywidth, ' '), value)


def main():
    parser = argparse.ArgumentParser(description="Get data from Eagle"
                                                 " Energy Gateway")
    parser.add_argument('address', help='Eagle Engergy Gateway address')
    parser.add_argument('-c', '--command', help='Command to send to gateway. '
                        'Available commands: {0}'.format(", ".join(COMMANDS)),
                        default='GET_DEVICE_DATA')
    args = parser.parse_args()
    try:
        gw = Gateway(args.address)
    except socket.error as e:
        sys.stderr.write(
            'Unable to connect to {0}. {1}\n'.format(args.address, e.strerror))
        sys.exit(1)
    display(gw.run_command(args.command)) 
    # print(gw.run_command_raw(args.command))
