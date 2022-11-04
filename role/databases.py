from typing import List

from pysyncobj.batteries import ReplDict

from ..models.databases import Partition, Schema
from .distribution import Distributed


class NoSQL(Partition):
    def get_tables(self) -> List[str]:
        data = self.retrieve("tables.json")
        return data

    def schema_exists(self) -> bool:
        return self.stat_object("schema.json")

    def create_table(self, table: str):
        self.available.append(table)

    def __init__(self, name: str):
        super().__init__(name)
        self.available = self.get_tables()


class TimeSeries(Partition):
    def __init__(self, name: str) -> None:
        super().__init__(name)


class Graph(Partition):
    def __init__(self, name: str) -> None:
        super().__init__(name)


class Relational(Partition):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.schema = Schema()


class Parameter(Partition):
    def __init__(self, name: str) -> None:
        super().__init__(name)


class Memory(Distributed):
    def __init__(self, name: str) -> None:
        Distributed.__init__(self, name)
        self.data = ReplDict
