from typing import Any, Callable, Dict, List, Union

from pysyncobj.batteries import ReplDict

from role.distribution import Distributed


class Messaging(Distributed):
    def __init__(self, name: str, consumers: List[str] = None):
        super().__init__(name, consumers)
        self.handlers: ReplDict[str, Dict[str, Callable]] = ReplDict()

    @replicated
    def route_message(self, message: Any, node: str = None):
        if not node:
            # If no node is specified, message is routed to the leader
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
