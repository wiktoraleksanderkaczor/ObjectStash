"""Pioneer setup script."""
import sys

import setuptools
from setuptools import find_packages

if sys.version_info < (3, 8):
    sys.exit("Sorry, Python < 3.8 is not supported")

DESCRIPTION = (
    "Multi-paradigm database, caching and FUSE layer on various storage clients, for example, S3, memory, local etc."
)

LONG_DESCRIPTION = """
Pioneer is a serverless distribution-capable database, caching, and FUSE layer self-contained package.

What can it do:
- It can act like a filesystem, mounted wherever needed for interfacing with legacy applications.
- It is also a storage client abstraction option; cloud, memory block or API.
- It can run a serverless multi-paradigm database on any storage client with online compute capabilities.
- It allows masterless peer-to-peer coordination for different distribution strategies.
- All of this with the ability to cache, replicate and shard as desired on any of the storage clients.
"""
setuptools.setup(
    name="Pioneer",
    version="0.1.0",
    url="https://github.com/wiktoraleksanderkaczor/Pioneer",
    author="Wiktor Kaczor",
    author_email="wiktoraleksanderkaczor@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(exclude=["tests"]),
    python_requires=">3.8.0",
    install_requires=[
        "minio",
        "zeroconf",
        "pysyncobj",
        "pyfuse",
        "pydantic",
        "PyYAML",
        "schedule",
        "python-magic",
        "jsonmerge",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
