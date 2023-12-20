"""
Data view protocol.
"""
from typing import Any, Iterator, List, Protocol, Tuple

from datamodel.data.path import FieldPath


class DataViewProtocol(Protocol):
    def get(self, path: FieldPath, default: Any = None) -> Any:
        ...

    def __getitem__(self, path: FieldPath) -> Any:
        ...

    def __setitem__(self, path: FieldPath, value: Any) -> None:
        ...

    def __delitem__(self, path: FieldPath) -> None:
        ...

    def __contains__(self, path: FieldPath) -> bool:
        ...

    def list(self, prefix: FieldPath) -> List[FieldPath]:
        ...

    def __iter__(self) -> Iterator[Tuple[FieldPath, Any]]:
        ...
