"""Vault interface."""
from abc import ABC, abstractmethod

from vault.models.parameter import Parameter


class VaultInterface(ABC):
    @abstractmethod
    def get(self, key: str) -> Parameter:
        ...

    @abstractmethod
    def set(self, key: str, value: Parameter) -> None:
        ...
