# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='tikki',
    version='0.999.dev0',
    description='Tikki Field Aptitude Performance Data Collection Platform',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='RESUL Ry',
    author_email='info@resul.fi',
    maintainer='Ville Brofeldt',
    maintainer_email='ville.brofeldt@streamroller.io',
    url='https://github.com/tikki-fi/tikki',
    include_package_data=True,
    license='MIT',
    entry_points={
        'console_scripts': [
            'tikki = tikki.__main__:main'
        ]
    },
    install_requires=[
        'alembic',
        'cryptography',
        'flask',
        'flask-cors',
        'flask-jwt-simple',
        'pandas',
        'pyjwt',
        'python-dateutil',
        'python-jose',
        'requests',
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
