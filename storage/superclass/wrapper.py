"""Wraps a storage client to provide additional functionality."""
from storage.interface.client import StorageClientInterface


class StorageWrapper:
    def __init__(self, wrapped: StorageClientInterface):
        self.wrapped = wrapped

    # Only called when not in current object, error when no such attr
    def __getattribute__(self, attr):
        return getattr(self.wrapped, attr)
