"""
Parameter database paradigm. Each parameter is stored as a key-value pair with tags.
"""
from typing import Callable, List, Tuple

from database.models.objects import JSON
from database.superclass.client import DatabaseClient
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey


class Parameter(DatabaseClient):
    def get(self, key: str) -> Tuple[JSON, JSON]:
        """
        Retrieve the value and tags associated with a given key from the database.

        Args:
            key (str): Item key for data retrieval.

        Returns:
            Tuple[JSON, JSON]: A tuple containing the value associated with the key in JSON format
            and the tags associated with the key in JSON format.
        """
        return (super().get(key), self.tags.get(key))

    def insert(self, key: str, value: Tuple[JSON, JSON]) -> None:
        """
        Insert a new record into the database with the given key and value.

        Args:
            key (str): The key to associate with the record.
            value (Tuple[JSON, JSON]): A tuple containing the value and tags to associate with the record.

        Returns:
            None
        """
        data, tags = value
        super().insert(key, data)
        self.tags.insert(key, tags)

    def select(self, condition: Callable[[Tuple[JSON, JSON]], bool]) -> List[Tuple[JSON, JSON]]:
        """
        Select records from the database based on a given condition.

        Args:
            condition (Callable[[Tuple[JSON, JSON]], bool]): A callable object that takes a tuple of a record's
                value and tags in JSON format, and returns a boolean indicating whether the record should be included
                in the result.

        Returns:
            List[Tuple[JSON, JSON]]: A list of tuples containing the value and tags associated with the records that
                meet the condition, in JSON format.
        """
        records = [self.get(key) for key in self.items()]
        records = list(filter(condition, records))
        return records

    def __init__(self, storage: StorageClientInterface, name: StorageKey):
        super().__init__(storage, name)
        self.tags = DatabaseClient(storage, name.join("tags"))
