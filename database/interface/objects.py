"""
This module defines the JSONProtocol class, a protocol for JSON serialization of custom classes.
"""
from abc import ABC, abstractmethod
from typing import Any

from typing_extensions import Self


class JSONProtocol(ABC):
    @abstractmethod
    def to_json(self) -> Any:
        """Converts the object to a JSON-compatible representation.

        Returns:
            Any: A JSON-compatible representation of the object.

        Note:
            This method must be implemented by a subclass in order to support JSON serialization.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("to_json() has not been implemented")

    @abstractmethod
    @classmethod
    def from_json(cls, json: Any) -> Self:
        """Constructs an instance of the class from a JSON representation.

        Args:
            json (Any): A JSON representation of an instance of the class.

        Returns:
            Self: An instance of the class.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("from_json() has not been implemented")
