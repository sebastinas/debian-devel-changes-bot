#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='debian-devel-changes-bot',
      packages=find_packages(),
      install_requires=['beautifulsoup4', 'python-debian', 'requests', 'pydbus'])
