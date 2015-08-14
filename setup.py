#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import py2exe
except ImportError:
    pass

from RESTool.RESTool_main import __version__


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='RESTool',
    version=__version__,
    description='Unofficial cross platform tool for migrating between browsers, backing up, and restoring from backups, "Reddit Enhancement Suite" aka RES settings.',
    long_description=readme + '\n\n' + history,
    author='Nikola Kovacevic',
    author_email='nikolak@outlook.com',
    url='https://github.com/nikola-k/RESTool',
    packages=[
        'RESTool',
    ],
    package_dir={'RESTool':
                 'RESTool'},
    entry_points={
        'console_scripts': [
            'RESTool = RESTool.RESTool_main:main',
        ],
    },
    app=['RESTool/RESTool_main.py'],
    windows=['RESTool/RESTool_main.py'],
    options={'py2app': {
        'argv_emulation': True
    }
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License",
    zip_safe=False,
    zipfile=None,
    keywords='RESTool',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop',
        'Environment :: X11 Applications :: Qt',
        'Topic :: Utilities',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
