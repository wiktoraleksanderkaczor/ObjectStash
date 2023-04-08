"""
Timeseries database paradigm is a database that stores data in a time series structure.
"""
from database.superclass.client import DatabaseClient
from storage.interface.client import StorageClientInterface


class Timeseries(DatabaseClient):
    def __init__(self, name: str, storage: StorageClientInterface) -> None:
        super().__init__(name, storage)
        raise NotImplementedError("Timeseries database has not been implemented yet")
