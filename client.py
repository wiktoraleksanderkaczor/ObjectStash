"""
Pioneer is a simple object storage system that allows you to store and retrieve objects from a variety of storage
backends. It is designed to be simple to use and easy to extend.

This module contains the main entry point for the Pioneer application.
"""
import signal

# from config.env import env
# from config.logger import log
from database.paradigms.nosql import NoSQL
from datamodel.data import JSON
from role.superclass.discovery import Coordinator
from storage.client.local import LocalClient
from storage.client.memory import MemoryClient
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StoragePath
from storage.wrapper.index import IndexWrapper


class GracefulExit:
    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, _signum, _frame):
        print("CTRL+C captured, exiting gracefully (repeat to exit unsafely)")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state


if __name__ == "__main__":
    # Start discovery and coordination
    coordinator: Coordinator = Coordinator()

    # Handle shutdowns
    flag: GracefulExit = GracefulExit()

    directory: StorageClientInterface = LocalClient(StoragePath("./local_data"))
    memory: StorageClientInterface = MemoryClient()

    ndb = NoSQL("random_db", directory)
    ndb.insert("test", JSON.parse_obj({"test": "test"}))
    indexed = IndexWrapper(directory, memory, [])

    indb = NoSQL("random_db", indexed)
    data = indb.get("test")

    print("")
