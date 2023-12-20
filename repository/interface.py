"""
Repository interface.
"""
from abc import ABC, abstractmethod
from typing import (
    Any,
    Generator,
    Generic,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Tuple,
    TypeVar,
)

from typing_extensions import Self

from storage.interface.client import StorageClientInterface
from storage.models.object.path import StorageKey

KT = TypeVar("KT")
VT = TypeVar("VT")


class RepositoryInterface(ABC, Generic[KT, VT]):
    @abstractmethod
    def __init__(self, name: str, storage: StorageClientInterface, *args, **kwargs) -> None:
        self.name: str
        self.storage: StorageClientInterface
        self.root: StorageKey
        self.data: StorageKey

    @abstractmethod
    def get(self, key: KT, default: Any = None) -> Optional[VT]:
        ...

    @abstractmethod
    def __getitem__(self, key: KT) -> VT:
        ...

    @abstractmethod
    def pop(self, key: KT, default: Any = None) -> Optional[VT]:
        ...

    @abstractmethod
    def popitem(self) -> Tuple[KT, VT]:
        ...

    # pylint: disable=arguments-differ
    @abstractmethod
    def update(self, other: MutableMapping[KT, VT]) -> None:
        ...

    @abstractmethod
    def __setitem__(self, name: KT, entity: VT) -> None:
        ...

    @abstractmethod
    def __delitem__(self, name: KT) -> None:
        ...

    @abstractmethod
    def setdefault(self, key: KT, default: Any = None) -> Optional[VT]:
        ...

    @abstractmethod
    def keys(self) -> List[KT]:
        ...

    @abstractmethod
    def values(self) -> Generator[VT, None, None]:
        ...

    @abstractmethod
    def items(self) -> Generator[Tuple[KT, VT], None, None]:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[KT]:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __contains__(self, key: KT) -> bool:
        ...

    @abstractmethod
    def __eq__(self, other: Self) -> bool:
        ...

    @abstractmethod
    def __ne__(self, other: Self) -> bool:
        ...
