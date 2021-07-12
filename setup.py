#!/usr/bin/env python
from os.path import abspath, dirname, join
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().strip().splitlines()


source_directory = dirname(abspath(__file__))

setup(
    name='checkio_client',
    version='0.2.15',
    python_requires='>=3.8',
    description='Command line interface for playing CheckiO games',
    author='CheckiO',
    author_email='a.lyabah@checkio.org',
    url='https://github.com/CheckiO/checkio-client',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['checkio = checkio_client.runner:main'],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
