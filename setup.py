from setuptools import setup

setup(
    name='pusher',
    version='0.6',
    description='A Python library for sending messages to Pusher',
    author='Pusher',
    author_email='support@pusher.com',
    url='http://pusher.com',
    packages=['pusher'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords='pusher rest realtime websockets service',
    license='MIT',
    install_requires=[
        'setuptools',
    ],
)
