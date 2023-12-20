"""
Flattened data view for internal services data model.
"""
from typing import Any, Iterator, List, Tuple

from datamodel.data.path import FieldPath
from datamodel.data.protocol.view import DataViewProtocol

FlatList = List[Tuple[FieldPath, Any]]


class FlatData(DataViewProtocol):
    def __init__(self, value: FlatList) -> None:
        self.data: FlatList = value

    def get(self, path: FieldPath, default: Any = None) -> Any:
        try:
            return self[path]
        except KeyError:
            return default

    def __getitem__(self, path: FieldPath) -> Any:
        for p, v in self.data:
            if p == path:
                return v
        raise KeyError(f"Key '{path}' does not exist")

    def __setitem__(self, path: FieldPath, value: Any) -> None:
        if path in self:
            self.data.remove((path, self[path]))
        # Remove affected
        affected = sorted(self.list(path), key=len)
        for p in affected:
            self.data.remove((p, self[p]))
        self.data.append((path, value))

    def __delitem__(self, path: FieldPath) -> None:
        self.data.remove((path, self[path]))

    def __contains__(self, path: FieldPath) -> bool:
        for p, _ in self.data:
            if p == path:
                return True
        return False

    def list(self, prefix: FieldPath) -> List[FieldPath]:
        paths = [p for p, _ in self.data if all(True for i, k in enumerate(prefix) if p[i] == k)]
        return sorted(paths, key=len)

    def __iter__(self) -> Iterator[Tuple[FieldPath, Any]]:
        return iter((p, self[p]) for p in self.list([]))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.data)})"

    def __str__(self) -> str:
        return repr(self)
