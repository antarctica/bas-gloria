###############################################################################
# Project: gloria
# Purpose: Packaging configuration for the gloria project
# Author:  Paul M. Breen
# Date:    2021-05-19
###############################################################################

from setuptools import setup

setup(name='gloria',
      version='0.1',
      description='Package for working with GLORIA files',
      url='https://gitlab.data.bas.ac.uk/pbree/gloria',
      author='Paul Breen',
      author_email='pbree@bas.ac.uk',
      license='Apache 2.0',
      packages=['gloria'],
      scripts=[
          'plot_gloria.py',
          'gloria_to_nc.py',
          'gloria_to_txt.py',
          'read_gloria.py',
          'write_gloria.py'
      ],
      install_requires=[
          'numpy',
          'netCDF4'
      ])

