#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

with open('README.md') as readme_file:
    readme = readme_file.read()

about = {}
with open(os.path.join(BASE_DIR, 'lenddo_api_client', '__version__.py')) as f:
    exec(f.read(), about)


requirements = []

test_requirements = []

setup_requirements = []

setup(
    name='lenddo',
    version=about['__version__'],
    description='Python library for integrating Lenddo Services. https://www.lenddo.com',
    long_description=readme,
    author='Lenddo',
    author_email='techbilling@lenddo.com',
    url='https://github.com/Lenddo/python-lenddo',
    packages=find_packages(),
    keywords='lenddo api client',
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
    ]
)

