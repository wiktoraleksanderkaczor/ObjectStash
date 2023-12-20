"""
Nested data view for internal services data model.
"""
from typing import Any, Dict, Iterator, List, Tuple, Union

from datamodel.data.path import FieldKey, FieldPath
from datamodel.data.protocol.view import DataViewProtocol

NestedDict = Dict[FieldKey, Union[Any, "NestedDict"]]


class NestedData(DataViewProtocol):
    def __init__(self, value: NestedDict) -> None:
        self.data: NestedDict = value

    def get(self, path: FieldPath, default: Any = None) -> Any:
        try:
            return self[path]
        except KeyError:
            return default

    def __getitem__(self, path: FieldPath) -> Any:
        data = self.data
        for key in path:
            data = data[key]
        return data

    def __setitem__(self, path: FieldPath, value: Any) -> None:
        if path in self:
            del self[path]
        # Remove affected
        affected = sorted(self.list(path), key=len)
        for p in affected:
            del self[p]
        data = self.data
        for key in path[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        data[path[-1]] = value

    def __delitem__(self, path: FieldPath) -> None:
        data = self.data
        for key in path[:-1]:
            data = data[key]
        del data[path[-1]]

    def __contains__(self, path: FieldPath) -> bool:
        data = self.data
        for key in path[:-1]:
            try:
                data = data[key]
            except KeyError:
                return False
        return path[-1] in data

    def list(self, prefix: FieldPath) -> List[FieldPath]:
        paths = []
        # Find root
        root = self.data
        for key in prefix:
            try:
                root = root[key]
            except KeyError:
                return []
        # List paths
        for key, value in root.items():
            path = [*prefix, key]
            if isinstance(value, dict):
                paths.extend(self.list(path))
            else:
                paths.append(path)
        paths = sorted(paths, key=len)
        return paths

    def __iter__(self) -> Iterator[Tuple[FieldPath, Any]]:
        return iter((p, self[p]) for p in self.list([]))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.data)})"

    def __str__(self) -> str:
        return repr(self)
