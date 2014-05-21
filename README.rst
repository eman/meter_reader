Meter Reader
===============================================================================

Meter Reader is a client library and command line client for retrieving
nearly realtime energy usage data from a smart meter via the Eagle™ Home
Energy Gateway. See
`Rainforest™ Automation <http://www.rainforestautomation.com>`_ for more
about the Eagle™ Home Energy Gateway.

Meter Reader is not affiliated with the Eagle™ Home Energy Gateway or
Rainforest™ Automation.

Installation
-------------------------------------------------------------------------------

.. code-block:: bash

    $ pip install meter-reader

Usage
-------------------------------------------------------------------------------
Meter Reader is intended to be used as a library for other applications
but it does contain a command line application called mr.

.. code-block:: bash

    $ mr < ip address >

This will run the ``LIST_DEVICES`` devices command on the gateway and display
a formatted response. Other commands, such as ``GET_DEVICE_DATA``, will first
run the ``LIST_DEVICES`` command to determine the MAC address of the gateway.

Commands can be specified with the '-c' option. For example::

    $ mr -c GET_DEVICE_DATA < ip address >

    MessageCluster
        DeviceMacId          xx:xx:xx:xx:xx:xx:xx:xx
        MeterMacId           xx:xx:xx:xx:xx:xx:xx
        TimeStamp            0
        Id                   0
        Priority             None
        Text                 None
        ConfirmationRequired N
        Confirmed            N
        Read                 Y
        Queue                active
    CurrentSummation
        DeviceMacId          xx:xx:xx:xx:xx:xx:xx:xx
        MeterMacId           xx:xx:xx:xx:xx:xx:xx
        TimeStamp            2014-04-19 16:01:22+00:00
        SummationDelivered   12949746
        SummationReceived    0
        Multiplier           1
        Divisor              1000
        DigitsRight          3
        DigitsLeft           15
        SuppressLeadingZero  Y
    NetworkInfo
    ...

::

    $ mr -c GET_SUMMATION_VALUES < ip address >

    2014-04-18 16:30:00+00:00, Summation, 0.350
    2014-04-18 17:30:00+00:00, Summation, 0.322
    2014-04-18 18:30:00+00:00, Summation, 0.193
    2014-04-18 19:30:00+00:00, Summation, 0.285
    2014-04-18 20:30:00+00:00, Summation, 0.286
    2014-04-18 21:30:00+00:00, Summation, 0.351
    ...

There are two ways to retrieve instantaneous demand:

1. Send the ``GET_INSTANTANEOUS_DEMAND`` command directly to the gateway. This
   will return a nearly raw response from the gateway (formatting is applied).

::

    $ mr -c GET_INSTANTANEOUS_DEMAND < ip address >

        InstantaneousDemand
        DeviceMacId         xx:xx:xx:xx:xx:xx:xx:xx
        MeterMacId          xx:xx:xx:xx:xx:xx:xx
        TimeStamp           2014-04-19 15:35:27+00:00
        Demand              297
        Multiplier          1
        Divisor             1000
        DigitsRight         3
        DigitsLeft          15
        SuppressLeadingZero Y

2. Supply the ``--get-instant-demand`` argument. This will post-process the
response before displaying it.::

    $ mr --get-instant-demand < ip address >

    2014-04-19 15:58:39+00:00, 0.292kW

Raw and unformatted data returned by the gatway, can be viewed by using the
'-r' option.

.. code-block:: bash

    $ mr -r -c GET_DEVICE_DATA < ip address >

Including Meter Reader in an application
-------------------------------------------------------------------------------

.. code-block:: python

    from meter_reader import Gateway

    GATEWAY_ADDRESS = '192.168.1.10'

    gw = Gateway(GATEWAY_ADDRESS)
    response = gw.run_command('GET_DEVICE_DATA')
    print('Network Info')
    print(response['NetworkInfo'])

    timestamp, demand = gw.get_instantaneous_demand()
    print('Demand {0!s} at {1!s}'.format(demand, timestamp))
