"""
Meter Reader
----------------------

Meter Reader is a client library and command line tool for retrieving
data from the Eagle Energy Gateway.

:copyright: (c) 2014 by Emmanuel Levijarvi
:license: BSD
"""

from setuptools import setup, find_packages
import codecs
import os


project_dir = os.path.abspath(os.path.dirname(__file__))

descriptions = []
for rst in ('README.rst', 'LICENSE.rst'):
    with codecs.open(os.path.join(project_dir, rst), 'r') as f:
        descriptions.append(f.read())


setup(name='meter-reader',
      version='1.0',
      description='Client Library for Eagle Energy Gateway',
      long_description='\n\n'.join(descriptions),
      author='Emmanuel Levijarvi',
      author_email='emansl@gmail.com',
      url='https://github.com/eman/meter_reader',
      packages=find_packages(),
      entry_points={'console_scripts': ['mr=meter_reader.client:main']},
      license="BSD",)
