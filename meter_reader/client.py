"""
Meter Reader

:copyright: (c) 2016 by Emmanuel Levijarvi
:license: BSD 2-Clause
"""

from __future__ import print_function
import sys
import argparse
from meter_reader.gateway import Gateway, GatewayError, COMMANDS
from meter_reader import __version__


def display(output):
    if isinstance(output, list):
        sys.stdout.write(', '.join(output[0]) + '\n')
        [print(', '.join([str(v) for v in i.values()])) for i in output]
    else:
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
    parser = argparse.ArgumentParser(
        prog='mr', description="Get data from Eagle Energy Gateway")
    parser.add_argument('address', help='Eagle Engergy Gateway address')
    parser.add_argument('-V', '--version', action='version',
                        version='mr {0}'.format(__version__))
    parser.add_argument('-r', '--raw', help='Display Raw, unparsed, response '
                        'from the Gateway', action='store_true')
    parser.add_argument('-c', '--command', help='Command to send to gateway. '
                        'Available commands: {0}'.format(", ".join(COMMANDS)),
                        default='GET_DEVICE_DATA', dest='Name')
    parser.add_argument('-i', '--interval', help='Total time period for '
                        'which samples are being requested. hour | day | week')
    parser.add_argument('-f', '--frequency', help="Requested number of seconds"
                        " between samples.", type=int)
    parser.add_argument('-s', '--start-time', dest='StartTime')
    parser.add_argument('-e', '--end-time', dest="EndTime")
    parser.add_argument('-d', '--duration', type=int)
    parser.add_argument('--get-instant-demand', action='store_true')
    args = parser.parse_args()
    try:
        gw = Gateway(args.address)
    except GatewayError as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    sys.stderr.write('\n')
    if args.get_instant_demand:
        ts, demand = (gw.get_instantaneous_demand())
        print("{0!s}, {1!s}kW".format(ts, demand))
        sys.exit(0)
    if args.raw:
        print(gw.run_command_raw(**vars(args)))
    else:
        display(gw.run_command(**vars(args)))
