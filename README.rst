Meter Reader
===============================================================================

Meter Reader is a client library and command line client for retrieving
data from the Eagle Energy Gateway.
See the following for more: http://www.rainforestautomation.com

Meter Reader is not affiliated with the Eagle Energy Gateway or
Rainforest Automation.

Installation
-------------------------------------------------------------------------------
Clone the the repository or download the zip archive and run
the following command::

    python setup.py install

Usage
-------------------------------------------------------------------------------
Meter Reader is intended to be used as a library for other applications
but it does contain a command line application called mr::

    mr < ip address >

This will run the LIST_DEVICES devices command on the gateway and display
a formatted response. Other commands, such as GET_DEVICE_DATA, will first
run the LIST_DEVICES command to determine the MAC address of the gateway.

Commands can be specified with the '-c' option. For example::

    mr -c GET_DEVICE_DATA < ip address >

Raw data, as returned by the gatway, can be viewed by using the '-r'
option::

    mr -r -c GET_DEVICE_DATA < ip address >

Including meter_reader in an application
-------------------------------------------------------------------------------
.. code-block:: python

    from meter_reader import Gateway

    GATEWAY_ADDRESS = '192.168.1.10'

    gw = Gateway(GATEWAY_ADDRESS)
    response = gw.run_command('GET_DEVICE_DATA')
    print('Network Info')
    print(response['NetworkInfo'])

    timestamp, demand = gw.get_instantaneous_demand()
    print('Demand {0} at {1}'.format(demand, timestamp))
