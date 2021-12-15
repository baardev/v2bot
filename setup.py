#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from os import environ as env
import subprocess

# from pip.req import parse_requirements
#
requirements = [str(req.req) for req in parse_requirements('requirements.txt', session=False)]
#
# try:
#     VERSION = subprocess.check_output(['git', 'describe', '--tags']).strip()
# except subprocess.CalledProcessError:
#     VERSION = '2.dev'

setup(
    name='v2bot',
    version=2,
    description="Crypto bot",
    long_description=open('README.md').read(),
    author="Jeff Milton",
    author_email='jwmilton@protonmail.com',
    url='',
    license='MIT',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'chatery = chatery:main',
        ],
    },
    zip_safe=False
)