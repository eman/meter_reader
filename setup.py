"""
Meter Reader
----------------------

Meter Reader is a command line client for retrieving data
from the Eagle Energy Gateway.

:copyright: (c) 2013 by Emmanuel Levijarvi
:license: BSD
"""

from distutils.core import setup

setup(name='Meter Reader',
      version='1.0',
      description='',
      author='Emmanuel Levijarvi',
      author_email='emansl@gmail.com',
      url='https://github.com/eman/meter_reader',
      py_modules=['meter_reader'],
      license="BSD",
      scripts=['meter_reader'],
)
