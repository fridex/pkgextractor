#!/usr/bin/python3

import sys
import os
from setuptools import setup, find_packages


if sys.version_info[0] != 3:
    sys.exit("Python3 is required in order to install pkgextract")


def get_requirements():
    with open('requirements.txt') as fd:
        return [item.split(' ')[0] for item in fd.read().splitlines()]


setup(
    name='pkgextract',
    version='1.0.0',
    entry_points={
        'console_scripts': ['pkgextract=pkgextract.cli:cli']
    },
    packages=find_packages(),
    install_requires=get_requirements(),
    author='Fridolin Pokorny',
    author_email='fridolin.pokorny@gmail.com',
    maintainer='Fridolin Pokorny',
    maintainer_email='fridolin.pokorny@gmail.com',
    description='Tool and library for interacting with GitHub API v3',
    url='https://github.com/fridex/pkgextract',
    license='ASL v2.0',
    keywords='docker dependencies package pypi rpm',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ]
)
