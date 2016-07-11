"""
Meter Reader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Meter Reader is a client library and command line tool for retrieving
smart meter data from an Eagle Energy Gateway.

:copyright: (c) 2016 by Emmanuel Levijarvi
:license: BSD 2-Clause
"""

from setuptools import setup, find_packages
import os


project_dir = os.path.abspath(os.path.dirname(__file__))

description = ('Client Library for retreiving smart meter data from an '
               'Eagle Energy Gateway')

long_descriptions = []
for rst in ('README.rst', 'LICENSE.rst'):
    with open(os.path.join(project_dir, rst), 'r') as f:
        long_descriptions.append(f.read())


setup(name='meter-reader',
      version='1.1.0',
      description=description,
      long_description='\n\n'.join(long_descriptions),
      author='Emmanuel Levijarvi',
      author_email='emansl@gmail.com',
      url='https://github.com/eman/meter_reader',
      license="BSD",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Home Automation',
          'Topic :: Utilities',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
      ],
      keywords='energy electricity smartmeter HAN',
      packages=find_packages(),
      entry_points={'console_scripts': ['mr=meter_reader.client:main']},)
