# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

from tikki.version import get_version

datadir = os.path.join('tikki', 'data')
datafiles = [(d, [os.path.join(d, f) for f in files])
             for d, folders, files in os.walk(datadir)]

with open('README.rst') as f:
    readme = f.read()

setup(
    name='tikki',
    version=get_version(),
    description='Tikki Field Aptitude Performance Data Collection Platform',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='RESUL Ry',
    author_email='info@resul.fi',
    maintainer='Ville Brofeldt',
    maintainer_email='ville.brofeldt@streamroller.io',
    url='https://github.com/tikki-fi/tikki',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs')),
    data_files=datafiles,
    install_requires=[
        'alembic',
        'flask',
        'flask-cors',
        'flask-jwt-simple',
        'pandas',
        'python-dateutil',
        'sqlalchemy',
        'sqlalchemy-utils',
        'werkzeug',
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ],
)
