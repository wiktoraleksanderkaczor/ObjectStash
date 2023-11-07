"""
This module defines the interface for distributed objects.
"""
from abc import ABC, abstractmethod

# from contextlib import contextmanager
from typing import Any, Callable, Set  # , Generator

from pydantic import AnyUrl


class DistributedInterface(ABC):
    peers: Set[AnyUrl]

    @abstractmethod
    def is_master(self) -> bool:
        ...

    @abstractmethod
    def on_master(self, func) -> Callable[..., Any]:
        ...

    # @abstractmethod
    # def is_synced(self) -> bool:
    #     ...

    # @abstractmethod
    # def sync(self) -> None:
    #     ...

    # @contextmanager
    # @abstractmethod
    # def transact(self, *args, **kwargs) -> Generator[None, Any, Any]:
    #     """
    #     A context manager that allows for atomic transactions on the distributed object.
    #     """

    @abstractmethod
    def __repr__(self) -> str:
        """
        Return the address of this instance, same initialization arguments on another
        server should return the same address. Server hostname and port not included.

        For example, if this instance was initialized with:
        LocalStorageClient(path="/tmp/test", timeout=30, grace=300)
        Then this method should return:
        LocalStorageClient(uuid) because those are meant to be unique
        """
