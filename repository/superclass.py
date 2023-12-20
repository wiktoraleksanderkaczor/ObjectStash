"""
Base class for all repositories.
"""
from abc import abstractmethod
from typing import (
    Any,
    Generator,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Tuple,
    TypeVar,
)

from typing_extensions import Self

from repository.interface import RepositoryInterface
from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey, StoragePath
from storage.wrapper.safety import SafetyWrapper

KT = TypeVar("KT")
VT = TypeVar("VT")


class BaseRepository(RepositoryInterface[KT, VT]):
    def __init__(self, name: str, storage: StorageClientInterface, *args, **kwargs) -> None:
        self.name: str = name
        self.storage: StorageClientInterface = SafetyWrapper(storage)
        self.root: StorageKey = StorageKey(storage=storage.name, path=StoragePath(path=f"{name}/"))

    def get(self, key: KT, default: Any = None) -> Optional[VT]:
        try:
            return self[key]
        except KeyError:
            return default

    @abstractmethod
    def __getitem__(self, key: KT) -> VT:
        ...

    def pop(self, key: KT, default: Any = None) -> Optional[VT]:
        try:
            data = self[key]
            del self[key]
            return data
        except KeyError:
            return default

    def popitem(self) -> Tuple[KT, VT]:
        keys = [key for key in self.keys() if key not in self.storage.RESERVED]
        key = keys[-1]
        data = self[key]
        del self[key]
        return key, data

    def update(self, other: MutableMapping[KT, VT]) -> None:
        for key, value in other.items():
            self[key] = value

    @abstractmethod
    def __setitem__(self, name: KT, entity: VT) -> None:
        ...

    @abstractmethod
    def __delitem__(self, name: KT) -> None:
        ...

    def setdefault(self, key: KT, default: Any = None) -> Optional[VT]:
        if key not in self:
            self[key] = default

        return self[key]

    @abstractmethod
    def keys(self) -> List[KT]:
        ...

    def values(self) -> Generator[VT, None, None]:
        for key in self:
            yield self[key]

    def items(self) -> Generator[Tuple[KT, VT], None, None]:
        for key in self:
            yield (key, self[key])

    def __iter__(self) -> Iterator[KT]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self.keys())

    def __contains__(self, key: KT) -> bool:
        return key in self.keys()

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, BaseRepository):
            return NotImplemented
        return self.name == other.name and self.storage == other.storage

    def __ne__(self, other: Self) -> bool:
        return not self == other
