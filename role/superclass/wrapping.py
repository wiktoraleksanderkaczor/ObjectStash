"""Base class for wrapping objects using 'wrapt' module"""
from typing import Any, List

from pysyncobj import SyncObjConsumer
from wrapt import ObjectProxy as WraptObjectProxy

from role.superclass.distribution import Distributed


class ObjectProxyMetaclass(type(WraptObjectProxy)):  # pylint: disable=too-few-public-methods
    pass


class DistributedObjectProxyMetaclass(type(WraptObjectProxy), type(Distributed)):
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
    def __init__(self, wrapped: Any, consumers: List[SyncObjConsumer]):
        ObjectProxy.__init__(self, wrapped)
        Distributed.__init__(self, f"{self.__class__}({repr(wrapped)})", consumers=consumers)
