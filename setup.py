# -*- coding: utf-8 -*-
from setuptools import setup
setup(
    name='pusher',
    version='1.3.0',
    description='A Python library to interract with the Pusher API',
    url='https://github.com/pusher/pusher-http-python',
    author='Pusher',
    author_email='support@pusher.com',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
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
        'pyasn1'
    ],

    tests_require=['nose', 'mock', 'HTTPretty'],

    extras_require={
        'aiohttp': ["aiohttp>=0.9.0"],
        'tornado': ['tornado>=4.0.0']
    },

    package_data={
        'pusher': ['cacert.pem']
    },

    test_suite='pusher_tests',
)
