"""
Distributed superclass for all distributed objects.
"""
from abc import ABC
from threading import Thread
from typing import Any, Callable, Set

import Pyro5.configure
import Pyro5.core
import Pyro5.nameserver
import Pyro5.server
from pydantic import AnyUrl
from Pyro5 import config as PyroConfig

from distribution.interface.distributed import DistributedInterface
from settings import config

PyroConfig.COMPRESSION = True  # type: ignore
PyroConfig.SERVERTYPE = "multiplex"  # type: ignore


class Distributed(DistributedInterface, ABC):
    daemon: Pyro5.server.Daemon = Pyro5.server.Daemon("0.0.0.0", config.distribution.port)
    nameserver: Pyro5.nameserver.NameServer = Pyro5.core.locate_ns(port=config.distribution.port)
    thread: Thread = Thread(target=daemon.requestLoop)
    peers: Set[AnyUrl] = set(config.distribution.peers)

    def __init__(self) -> None:
        # Register this instance with the daemon
        uri = self.daemon.register(self)

        # self.address or repr(self)?
        self.nameserver.register(repr(self), uri)

        # Start the daemon thread if it is not already running
        if not self.thread.is_alive():
            self.thread.start()

    def __del__(self) -> None:
        self.nameserver.remove(repr(self))
        self.daemon.unregister(repr(self))

    def is_master(self) -> bool:
        ...

    def on_master(self, func) -> Callable[..., Any]:
        def wrapper(*args, **kwargs):
            if self.is_master():
                return func(*args, **kwargs)
            return lambda *args, **kwargs: None

        return wrapper
