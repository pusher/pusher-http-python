# -*- coding: utf-8 -*-
from setuptools import setup
import os
import re

# Lovingly adapted from https://github.com/kennethreitz/requests/blob/39d693548892057adad703fda630f925e61ee557/setup.py#L50-L55
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pusher/version.py'), 'r') as fd:
    VERSION = re.search(r'^VERSION = [\']([^\']*)[\']',
                        fd.read(), re.MULTILINE).group(1)

if not VERSION:
    raise RuntimeError('Ensure `VERSION` is correctly set in ./pusher/version.py')

setup(
    name='pusher',
    version=VERSION,
    description='A Python library to interract with the Pusher Channels API',
    long_description='A Python library to interract with the Pusher Channels API',
    long_description_type='text/x-rst',
    url='https://github.com/pusher/pusher-http-python',
    author='Pusher',
    author_email='support@pusher.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='pusher rest realtime websockets service',
    license='MIT',

    packages=[
        'pusher'
    ],

    install_requires=[
        'six',
        'requests>=2.3.0',
        'urllib3',
        'pyopenssl',
        'ndg-httpsclient',
        'pyasn1',
        'pynacl'
    ],

    tests_require=['nose', 'mock', 'HTTPretty'],

    extras_require={
        'aiohttp': ['aiohttp>=0.20.0'],
        'tornado': ['tornado>=5.0.0']
    },

    package_data={
        'pusher': ['cacert.pem']
    },

    test_suite='pusher_tests',
)
