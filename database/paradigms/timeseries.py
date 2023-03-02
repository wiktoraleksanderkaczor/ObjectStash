"""
Timeseries database paradigm is a database that stores data in a time series structure.
"""
from database.models.database import Database
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey


class Timeseries(Database):
    def __init__(self, storage: StorageClientInterface, name: StorageKey) -> None:
        super().__init__(storage, name)
        raise NotImplementedError("Timeseries database has not been implemented yet")
