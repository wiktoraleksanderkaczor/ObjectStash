from typing import Any, Callable, Dict, List

from pysyncobj import replicated
from pysyncobj.batteries import ReplPriorityQueue

from role.distribution import Distributed


class Messaging(Distributed):
    def process(self):
        item: Dict[str, Any] = self.queue.get()
        if item:
            name: str = item.get("handler")
            func: Callable = self.handlers.get(name)
            args = item.get("args", [])
            kwargs = item.get("kwargs", {})
            if func:
                func(*args, **kwargs)

    def __init__(self, name):
        Distributed.__init__(self, name)
        self.queue = ReplPriorityQueue()
        self.handlers: Dict[str, Callable] = {}
        self.addOnTickCallback(self.process)

    @replicated
    def send(self, handler: str, args: List[Any] = None, kwargs: Dict[str, Any] = None):
        item = {"handler": handler}
        if args:
            item["args"] = args
        if kwargs:
            item["kwargs"] = kwargs

        self.queue.put(item)

    def add_handler(self, name: str, func: Callable):
        self.handlers[name] = func
