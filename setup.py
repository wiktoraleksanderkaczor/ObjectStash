import setuptools
from setuptools import find_packages

DESCRIPTION = 'Timeseries, NoSQL and Graph database exclusively on S3 or other compatible storage'
setuptools.setup(
    name='ObjectStash',
    version='0.1.0',
    url='https://github.com/wiktoraleksanderkaczor/ObjectStash',
    author='Wiktor Kaczor',
    author_email='wiktoraleksanderkaczor@gmail.com',
    description=DESCRIPTION,
    long_description=open('DESCRIPTION.rst').read(),
    packages=find_packages,
    package_data={'': ['*.yaml']},
    install_requires=['minio', 'zeroconf', 'pysyncobj', 'pyfuse'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True,
    package_data={'': ['data/*.csv']},
)
