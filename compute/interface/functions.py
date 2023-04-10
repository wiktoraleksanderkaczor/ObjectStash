"""Interface for function clients."""
from abc import ABC, abstractmethod

from compute.models.functions.client import FunctionClientStatus
from compute.models.functions.config import FunctionConfig
from compute.models.functions.event import FunctionEvent, FunctionResponse
from storage.interface.client import StorageClientInterface


class FunctionClientInterface(ABC):
    @abstractmethod
    def __init__(self, storage: StorageClientInterface):
        self.storage: StorageClientInterface

    def status(self) -> FunctionClientStatus:
        ...

    @abstractmethod
    def run(self, func: FunctionConfig, event: FunctionEvent) -> FunctionResponse:
        ...
