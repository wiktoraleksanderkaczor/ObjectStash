"""
This module contains the configuration for the application.
"""
from dataclasses import _MISSING_TYPE, MISSING, dataclass, field
from datetime import timedelta
from typing import Union


@dataclass
class ClusterConfig:
    name: str = "default"


@dataclass
class LockingConfig:
    duration: timedelta = timedelta(seconds=5)


@dataclass
class StorageConfig:
    _target_: Union[_MISSING_TYPE, str] = MISSING
    locking: LockingConfig = field(default_factory=LockingConfig)


@dataclass
class DatabaseConfig:
    storage: StorageConfig = field(default_factory=StorageConfig)


@dataclass
class InterfaceConfig:
    port: int = 9090


@dataclass
class DistributionConfig:
    port: int = 9091
    peers: list = field(default_factory=list)


@dataclass
class Config:
    cluster: ClusterConfig = field(default_factory=ClusterConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    interface: InterfaceConfig = field(default_factory=InterfaceConfig)
    distribution: DistributionConfig = field(default_factory=DistributionConfig)


config: Config = Config()
