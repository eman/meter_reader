"""
Meter Reader

:copyright: (c) 2014 by Emmanuel Levijarvi
:license: BSD
"""

from __future__ import print_function
import sys
import argparse
from meter_reader.gateway import Gateway, GatewayError, COMMANDS


COMMANDS = ['LIST_DEVICES', 'GET_DEVICE_DATA', 'GET_INSTANTANEOUS_DEMAND',
            'GET_DEMAND_VALUES', 'GET_SUMMATION_VALUES']


def display(output):
    keywidth = 0
    for section in output:
        for key in output[section]:
            if len(key) > keywidth:
                keywidth = len(key)
    for section in output:
        print(section)
        for key, value in list(output[section].items()):
            print(' ' * 3, key.ljust(keywidth, ' '), value)


def main():
    parser = argparse.ArgumentParser(description="Get data from Eagle"
                                                 " Energy Gateway")
    parser.add_argument('address', help='Eagle Engergy Gateway address')
    parser.add_argument('-r', '--raw', help='Display Raw, unparsed, response '
                        'from the Gateway', action='store_true')
    parser.add_argument('-c', '--command', help='Command to send to gateway. '
                        'Available commands: {0}'.format(", ".join(COMMANDS)),
                        default='GET_DEVICE_DATA')
    args = parser.parse_args()
    try:
        gw = Gateway(args.address)
    except GatewayError as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    if args.raw:
        print(gw.run_command_raw(args.command))
    else:
        display(gw.run_command(args.command))
