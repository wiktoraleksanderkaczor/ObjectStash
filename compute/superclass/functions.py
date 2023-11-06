"""Base class for function clients"""
from abc import abstractmethod

from compute.interface.functions import FunctionClientInterface
from compute.models.functions.client import FunctionClientStatus
from compute.models.functions.config import FunctionConfig
from compute.models.functions.event import FunctionEvent, FunctionResponse
from storage.interface.client import StorageClientInterface


class FunctionClientBase(FunctionClientInterface):
    def __init__(self, storage: StorageClientInterface):
        self.storage: StorageClientInterface = storage

    @abstractmethod
    def status(self) -> FunctionClientStatus:
        ...

    @abstractmethod
    def run(self, func: FunctionConfig, event: FunctionEvent) -> FunctionResponse:
        if func.storage != self.storage.name:
            raise ValueError("Function storage does not match client storage")
