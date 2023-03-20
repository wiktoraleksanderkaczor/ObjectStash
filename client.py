"""
Pioneer is a simple object storage system that allows you to store and retrieve objects from a variety of storage
backends. It is designed to be simple to use and easy to extend.

This module contains the main entry point for the Pioneer application.
"""
import signal
from pathlib import PurePosixPath
from typing import Type, Union

from config.env import env
from config.logger import log
from config.models.env import StorageConfig
from database.models.objects import JSON
from database.paradigms.nosql import NoSQL
from role.superclass.discovery import Coordinator
from storage.client.local import LocalClient
from storage.client.memory import MemoryClient
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey
from storage.wrapper.index import IndexWrapper


class GracefulExit:
    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, _signum, _frame):
        print("CTRL+C captured, exiting gracefully (repeat to exit now)")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state


class StorageManager:
    def __init__(self, client: StorageClientInterface):
        self.client: StorageClientInterface = client
        log.debug("Initializing with the %s repository", client.config.repository)

    def database(self):
        pass

    def filesystem(self):
        pass


class Pioneer:
    def __init__(self):
        self.coordinator = Coordinator()
        self.flag = GracefulExit()

    def connect(
        self, config: Union[str, StorageConfig], client: Type[StorageClientInterface]
    ) -> StorageClientInterface:
        settings: Union[StorageConfig, None] = None
        if isinstance(config, str):
            settings = env.storage.get(config, None)
        else:
            settings = config

        if not settings:
            raise KeyError(f"{config} not found in settings or arguments")

        if not client:
            raise KeyError(f"{config} not found in available storage clients")

        try:
            instance: StorageClientInterface = client(settings)
            return instance
        except Exception as e:
            raise RuntimeError(f"{client.__name__} initialisation failed: {e}") from e

    def __del__(self):
        del self.coordinator
        return self.flag


if __name__ == "__main__":
    pioneer = Pioneer()

    directory = pioneer.connect("Local", LocalClient)
    memory = pioneer.connect("Memory", MemoryClient)

    db_key = StorageKey(storage=directory.name, path=PurePosixPath("random_db"))
    ndb = NoSQL(directory, db_key)
    ndb.insert("test", JSON.parse_obj({"test": "test"}))
    indexed = IndexWrapper(directory, memory, [])

    indb = NoSQL(indexed, db_key)
    data = indb.get("test")

    print("")
