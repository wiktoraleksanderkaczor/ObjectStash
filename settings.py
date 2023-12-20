"""
This module contains the configuration for the application.
"""
import os
from datetime import timedelta

from datamodel.data.model import Data, Field


class ClusterConfig(Data):
    name: str = "default"


class LockingConfig(Data):
    duration: timedelta = timedelta(seconds=5)


class StorageConfig(Data):
    _target_: str = "storage.client.memory.MemoryClient"
    locking: LockingConfig = Field(default_factory=LockingConfig)


class DatabaseConfig(Data):
    storage: StorageConfig = Field(default_factory=StorageConfig)


class InterfaceConfig(Data):
    port: int = 9090


class DistributionConfig(Data):
    port: int = 9091
    peers: list = Field(default_factory=list)


class RuntimeConfig(Data):
    debug: bool = False


class Config(Data):
    cluster: ClusterConfig = Field(default_factory=ClusterConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    interface: InterfaceConfig = Field(default_factory=InterfaceConfig)
    distribution: DistributionConfig = Field(default_factory=DistributionConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)


config_file: str = os.environ.get("VINT_CONFIG_FILE", "config.json")
config: Config

with open(config_file, "r", encoding="utf-8") as handle:
    config = Config.from_raw(handle.read())
