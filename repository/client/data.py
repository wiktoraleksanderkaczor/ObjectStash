"""
Data repository implementation.
"""
from typing import List

from datamodel.data.model import Data
from repository.superclass import BaseRepository
from storage.models.object.models import Object


class DataRepository(BaseRepository[str, Data]):
    def __getitem__(self, key: str) -> Data:
        raw = self.storage.get(self.root.join(key))
        return Data.from_raw(raw)

    def __setitem__(self, name: str, entity: Data) -> None:
        key = self.root.join(name)
        obj, data = Object.create_file(key, entity.to_json().encode())
        if name in self:
            self.storage.remove(key)
        self.storage.put(obj, data)

    def __delitem__(self, name: str) -> None:
        self.storage.remove(self.root.join(name))

    def keys(self) -> List[str]:
        items = self.storage.list(self.root)
        names = [item.path.name for item in items if item.path not in self.storage.RESERVED]
        return names
