from storage.models.client import StorageClient


class StorageWrapper:
    def __init__(self, wrapped: StorageClient):
        self.wrapped = wrapped

    # Only called when not in current object, error when no such attr
    def __getattribute__(self, attr):
        return getattr(self.wrapped, attr)
