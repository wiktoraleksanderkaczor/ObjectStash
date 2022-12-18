from typing import List

from database.models.database import Database


class NoSQL(Database):
    def get_tables(self) -> List[str]:
        data = self.get("tables.json")
        return data

    def schema_exists(self) -> bool:
        return self.stat_object("schema.json")

    def create_table(self, table: str):
        self.available.append(table)

    def __init__(self, name: str):
        super().__init__(name)
        self.available = self.get_tables()
