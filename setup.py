__version__ = '2.0dev'
import os

try:
    from distribute_setup import use_setuptools
    use_setuptools()
except:  # doesn't work under tox/pip
    pass

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='pusher',
    version=__version__,
    description='A Python library for sending messages to Pusher',
    author='Pusher',
    author_email='support@pusher.com',
    url='http://pusher.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
        classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords='pusher rest realtime websockets service',
    license='MIT',
)
