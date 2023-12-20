"""
This module contains the implementation of an overlay wrapper for the storage client.
"""
from enum import Enum
from typing import List

from storage.interface.client import StorageClientInterface
from storage.models.object.file.data import FileData
from storage.models.object.models import Object
from storage.models.object.path import StorageKey
from storage.wrapper.interface import StorageWrapper


class ShardStrategy(str, Enum):
    MOST_FREE = "most_free"
    LEAST_FREE = "least_free"
    ROUND_ROBIN = "round_robin"


class ShardedWrapper(StorageWrapper):
    def __init__(
        self,
        wrapped: StorageClientInterface,
        shard: StorageClientInterface,
        strategy: ShardStrategy = ShardStrategy.MOST_FREE,
    ):
        super().__init__(wrapped)
        self.shard: StorageClientInterface = shard
        self.strategy: ShardStrategy = strategy

    def get(self, key: StorageKey) -> FileData:
        if key.storage == self.shard.name:
            return self.shard.get(key)
        if key.storage == self.__wrapped__.name:
            return self.__wrapped__.get(key)
        raise ValueError(f"Key {key} does not belong to this shard")

    def put(self, obj: Object, data: FileData) -> None:
        if obj.key.storage == self.shard.name:
            self.shard.put(obj, data)
        if obj.key.storage == self.__wrapped__.name:
            self.__wrapped__.put(obj, data)
        raise ValueError(f"Key {obj.key} does not belong to this shard")

    def remove(self, key: StorageKey) -> None:
        if key.storage == self.shard.name:
            self.shard.remove(key)
        elif key.storage == self.__wrapped__.name:
            self.__wrapped__.remove(key)
        else:
            raise ValueError(f"Key {key} does not belong to this shard")

    def stat(self, key: StorageKey) -> Object:
        if key.storage == self.shard.name:
            return self.shard.stat(key)
        if key.storage == self.__wrapped__.name:
            return self.__wrapped__.stat(key)
        raise ValueError(f"Key {key} does not belong to this shard")

    def list(self, prefix: StorageKey, recursive: bool = False) -> List[StorageKey]:
        if prefix.storage == self.shard.name:
            return self.shard.list(prefix, recursive)
        if prefix.storage == self.__wrapped__.name:
            return self.__wrapped__.list(prefix, recursive)
        raise ValueError(f"Key {prefix} does not belong to this shard")
