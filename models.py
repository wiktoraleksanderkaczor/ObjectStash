
from typing import Dict, List

from pysyncobj.batteries import ReplDict

from .partition import Partition
from .distribution import Distributed
from .storage import storage


class Schema(Partition):
    def __init__(self) -> None:
        self.fname: str = 'schema.json'
        self.schema: Dict[str, str] = None
        if storage.object_exists(self.fname):
            self.schema = storage.get_object(self.fname)
        else:
            self.schema = {}
            storage.put_object(self.fname, self.schema)


class Table(Partition):
    def __init__(self, name: str):
        super().__init__(name)

    def select_by_value(val: dict):
        pass


class NoSQL(Partition):
    def get_tables(self) -> List[str]:
        data = self.retrieve('tables.json')
        return data

    def schema_exists(self) -> bool:
        return self.stat_object('schema.json')

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
