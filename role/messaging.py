from typing import Any, Callable, Dict, List

from pysyncobj import replicated

from ..models.databases import JSONish
from ..role.distribution import Distributed


class Messaging(Distributed):
    handling: Dict[str, Callable] = {"invalidate_cache": None}
    targets: Dict[str, List[object]]

    def process(self):
        for msg in self.queue:
            name: str = msg.get("func")
            func: Callable = Messaging.handling.get(name)
            if not func:
                continue

    def __init__(self, name):
        Distributed.__init__(self, name)
        self.queue: List[Dict[str, Any]] = []
        self.addOnTickCallback(self.process)

    @replicated
    def send(self, msg: JSONish):
        self.queue.append(msg)
