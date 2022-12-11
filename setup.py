import setuptools
from setuptools import find_packages

DESCRIPTION = (
    "Multi-paradigm database, caching and FUSE layer on various storage clients, for example, S3, memory, local etc."
)
setuptools.setup(
    name="ObjectStash",
    version="0.1.0",
    url="https://github.com/wiktoraleksanderkaczor/ObjectStash",
    author="Wiktor Kaczor",
    author_email="wiktoraleksanderkaczor@gmail.com",
    description=DESCRIPTION,
    long_description=open("DESCRIPTION.rst").read(),
    packages=find_packages(exclude=("tests")),
    install_requires=["minio", "zeroconf", "pysyncobj", "pyfuse", "pydantic", "PyYAML"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
