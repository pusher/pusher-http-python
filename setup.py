from setuptools import setup

setup(
    name='pusher',
    version='0.4',
    description='A Python library for sending messages to Pusher',
    author='New Bamboo',
    author_email='info@new-bamboo.co.uk',
    url='http://pusherapp.com',
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