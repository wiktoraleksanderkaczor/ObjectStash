# Defines a model for persistency, operations like cache.get and cache.set for raw data, bytes essentially, compatible

from pydantic import Protocol


class Persistence(Protocol):
    def get():
        ...

    def set():
        ...

    def remove():
        ...
