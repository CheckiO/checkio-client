#!/usr/bin/env python
from os.path import abspath, dirname, join
from setuptools import setup, find_packages


source_directory = dirname(abspath(__file__))

setup(
    name='checkio_client',
    version='0.1.12',
    python_requires='>=3.5',
    description='Command line interface for playing CheckiO games',
    author='CheckiO',
    author_email='a.lyabah@checkio.org',
    url='https://github.com/CheckiO/checkio-client',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['checkio = checkio_client.runner:main'],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
