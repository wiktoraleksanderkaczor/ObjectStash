from typing import List

from pydantic import Protocol

from role.distribution import Distributed
from storage.client.models.objects import Object


class Distribution(Distributed, Protocol):
    # Returns node to store a particular object on. Default should be local.
    def on(obj: Object) -> List[str]:
        ...
