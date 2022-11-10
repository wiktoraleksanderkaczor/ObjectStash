from pydantic import Protocol

from storage.client.models.objects import Object


class Distribution(Protocol):
    # Returns node to store a particular object on. Default should be local.
    def on(obj: Object) -> str:
        ...
