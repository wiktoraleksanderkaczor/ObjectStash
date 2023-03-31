"""Discovery role interfaces."""
from abc import ABC, abstractmethod

from pydantic import AnyUrl
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf


class ListenerInterface(ABC):
    @abstractmethod
    def update_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        ...

    @abstractmethod
    def remove_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        ...

    @abstractmethod
    def add_service(self, zc: Zeroconf, type_: str, name: AnyUrl) -> None:
        ...


class CoordinatorInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.zeroconf: Zeroconf
        self.listener: ListenerInterface
        self.browser: ServiceBrowser
        self.service: ServiceInfo

    @abstractmethod
    def __del__(self):
        ...
