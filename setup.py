#!/usr/bin/env python
from os.path import abspath, dirname, join
from setuptools import setup, find_packages


source_directory = dirname(abspath(__file__))

setup(
    name='checkio_client',
    version='0.0.1',
    description='CheckiO command line interface for playing CheckiO',
    author='CheckiO',
    author_email='a.lyabah@checkio.org',
    url='https://github.com/CheckiO/checkio-client',
    download_url='https://github.com/CheckiO/checkio-client/tarball/0.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['checkio = checkio_client.runner:main'],
    },
)
