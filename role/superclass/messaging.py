from typing import Any, Callable, Union

from pysyncobj.batteries import ReplDict, replicated

from role.interface.messaging import MessagingInterface
from role.superclass.distribution import Distributed


class Messaging(MessagingInterface, Distributed):
    def __init__(self, name: str):
        self.handlers: ReplDict = ReplDict()  # [str, Dict[str, Callable]]
        Distributed.__init__(self, name, consumers=[self.handlers])

    @replicated
    def route_message(self, message: Any, node: str = "leader"):
        if node == "leader" or not node:
            # If node is leader or no node specified, message is routed to the leader
            node = self.getStatus()["leader"]
        if node == self.selfNode:
            # If the node is the same as the current node, handle message locally
            self.handle_message(message)

    @replicated
    def add_message_handler(self, name: str, filter: Callable, func: Callable):
        self.handlers[name] = {"filter": filter, "func": func}

    def remove_message_handler(self, name: str) -> Union[str, None]:
        return self.handlers.pop(name, None)

    def handle_message(self, message: Any):
        for handling in self.handlers.values():
            if handling["filter"](message):
                return handling["func"](message)


messaging = Messaging("Messaging")
