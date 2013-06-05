"""
Eagle Gateway Client
----------------------

Eagle Gateway Client is a command line client for retrieving data
from the Eagle Energy Gateway.

:copyright: (c) 2013 by Emmanuel Levijarvi
:license: BSD
"""

from distutils.core import setup

setup(name='Eagle Gateway Client',
      version='1.0',
      description='Command-line client for Eagle Gateway, from Rainforest.',
      author='Emmanuel Levijarvi',
      author_email='emansl@gmail.com',
      py_modules=['eagle_gateway'],
      license="BSD",
      scripts=['eagle_client'],
)
