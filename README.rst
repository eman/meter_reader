Meter Reader
============================

This is an early attempt at pulling data from an Eagle Energy Gateway.
See the following for more: http://www.rainforestautomation.com

Meter Reader is not affiliated with the Eagle Energy Gateway or
Rainforest Automation.

Installation
------------------------
Clone the the repository or download the zip archive and run
the following command::

    python setup.py install

Usage
------------------------
.. code-block::

    meter_reader < ip address >

This will run the LIST_DEVICES devices command on the gateway and display
a formatted response. Other commands, such as GET_DEVICE_DATA, will first
run the LIST_DEVICES command to determine the MAC address of the gateway.

Commands can be specified with the '-c' option. For example::

    meter_reader -c GET_DEVICE_DATA < ip address >

Raw data, as resturned by the gatway, can be viewed by using the '-r'
option::

    meter_reader -r GET_DEVICE_DATA < ip address > 
