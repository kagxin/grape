#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
readme_file = os.path.join(here, 'README.md')

long_description = '\n\n'.join((
    open(readme_file).read(),
))


setup(
    name = 'grape',
    version = '0.0.1',
    url = 'http://github.com/kagxin/grape',
    license = 'BSD',
    description = 'Remote logging support for django.',
    long_description = long_description,
    author = "kagxin",
    author_email = 'kagxin at gmail dot com',
    packages = ['grape'],
    # py_modules = ['grape/management/commands/grape_client'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    zip_safe = True,
    install_requires = ['setuptools', "six"],
)
