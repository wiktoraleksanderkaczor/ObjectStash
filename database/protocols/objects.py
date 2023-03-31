"""Protocols for custom objects that can be stored in the database."""
from abc import abstractmethod
from typing import Any, Protocol


class JSONProtocol(Protocol):
    def json(self) -> str:
        ...

    @classmethod
    @abstractmethod
    def from_json(cls, value: str) -> Any:
        ...
