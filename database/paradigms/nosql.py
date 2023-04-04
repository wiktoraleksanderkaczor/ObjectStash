"""
NoSQL database paradigm is a database that stores data in a document structure.
"""
from database.superclass.client import DatabaseClient


class NoSQL(DatabaseClient):
    def namespace(self, name: str) -> "NoSQL":
        """
        Create a new namespace in the database.

        Args:
            name (str): Name of the namespace.

        Returns:
            NoSQL: A new NoSQL database client.
        """
        return NoSQL(self.storage, self.prefix.join(name))
