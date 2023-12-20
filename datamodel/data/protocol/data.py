"""
Defines the DataProtocol interface for [de]serialization.
"""
from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from typing_extensions import Self

if TYPE_CHECKING:
    from datamodel.data.model import Data


@runtime_checkable
class DataProtocol(Protocol):
    @abstractmethod
    def to_data(self) -> "Data":
        """Converts the object to a Data-compatible representation.

        Returns:
            Data: A Data-compatible representation of the object.

        Note:
            This method must be implemented by a subclass in order to support Data serialization.
        """
        raise NotImplementedError("to_data() has not been implemented")

    @classmethod
    @abstractmethod
    def from_data(cls, value: "Data") -> Self:
        """Constructs an instance of the class from a Data representation.

        Args:
            data (Data): A Data representation of an instance of the class.

        Returns:
            Self: An instance of the class.
        """
        raise NotImplementedError("from_data() has not been implemented")
