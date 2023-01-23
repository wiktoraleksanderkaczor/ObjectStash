from abc import ABC, abstractmethod
from typing import Any, Callable, Union

from pysyncobj.batteries import ReplDict, replicated


class MessagingInterface(ABC):
    @abstractmethod
    def __init__(self, name: str):
        self.handlers: ReplDict  # [str, Dict[str, Callable]]

    @replicated
    @abstractmethod
    def route_message(self, message: Any, node: str = "leader"):
        ...

    @replicated
    @abstractmethod
    def add_message_handler(self, name: str, filter: Callable, func: Callable):
        ...

    @abstractmethod
    def remove_message_handler(self, name: str) -> Union[str, None]:
        ...

    @abstractmethod
    def handle_message(self, message: Any):
        ...


messaging: MessagingInterface
