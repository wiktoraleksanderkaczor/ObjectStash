"""Base class for wrapping objects using 'wrapt' module"""
from typing import Any, List

from pysyncobj import SyncObjConsumer
from wrapt import ObjectProxy as WraptObjectProxy

from network.superclass.distribution import Distributed


class ObjectProxyMetaclass(type(WraptObjectProxy)):  # pylint: disable=too-few-public-methods
    pass


class DistributedObjectProxyMetaclass(ObjectProxyMetaclass, type(Distributed)):
    pass


class ObjectProxy(WraptObjectProxy):
    def __init__(self, wrapped: Any):
        WraptObjectProxy.__init__(self, wrapped)

    def __copy__(self):
        ...

    def __deepcopy__(self, memo):
        ...

    def __reduce__(self):
        ...

    def __reduce_ex__(self, protocol):
        ...


class DistributedObjectProxy(ObjectProxy, Distributed, metaclass=DistributedObjectProxyMetaclass):
    """
    Base class for distributed object proxies. Wrapped class must inherit `Distributed` class
    """

    def __init__(self, wrapped: Any, consumers: List[SyncObjConsumer]):
        # Make this object a proxy for the underlying object
        ObjectProxy.__init__(self, wrapped)
        # Make underlying object a distributed object
        Distributed.__init__(self, repr(self), consumers=consumers)
