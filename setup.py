"""
Meter Reader
----------------------

Meter Reader is a command line client for retrieving data
from the Eagle Energy Gateway.

:copyright: (c) 2014 by Emmanuel Levijarvi
:license: BSD
"""

from distutils.core import setup

setup(name='meter_reader',
      version='1.0',
      description='',
      author='Emmanuel Levijarvi',
      author_email='emansl@gmail.com',
      url='https://github.com/eman/meter_reader',
      packages=['meter_reader'],
      license="BSD",
      scripts=['mr'],)
