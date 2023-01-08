"""
StorageClient is the base class for all storage clients. It consists of a set of required and optional functions.
Multiple-based variants of those operations are also available. Those can act on the following base types:
- Object
- Directory
- Container
- Item (superset of Object and Directory)

Options can be:
    - get
    - list
    - put
    - remove
    - stat
    - exists
    ... and {operation}_multiple versions of the above
"""
from typing import Dict, List, Type, Union

from storage.models.client.key import StorageClientKey
from storage.models.item.data import ObjectData
from storage.models.item.models import Directory, Object
from storage.models.item.paths import DirectoryPath, ObjectPath, StorageKey
from storage.models.medium import Medium
from storage.models.repository import Repository

ITEM = Union[Object, Directory]


class StorageClient:
    clients: Dict[StorageClientKey, "StorageClient"] = {}
    subclasses: Dict[str, Type["StorageClient"]] = {}

    def __init__(
        self,
        repository: Repository,
        *args,
        **kwargs,
    ):
        self.client = None
        self.repository = repository
        self.clients[self.name] = self

    def __init_subclass__(cls: Type["StorageClient"], **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.__name__] = cls

    # REQUIRED:
    # TODO: Initial container setup methods... since MinIO has create_bucket which seems separate from other operations.
    # This also means that ContainerPath will not be dependant on StorageKey... probably? Although, I suppose it could.
    # Also figure out a way to store connected clients... especially for the whole StorageKey client for URL replace.
    # Like so; {client_name}@{container(UUID)}://{path} with UUID being generated and stored per container.
    # Streams will be implemented over PyFuse, too much bullshit otherwise...
    # Should I put ObjectData in Object under a generator?

    def get(self, key: ObjectPath) -> ObjectData:
        ...

    def stat(self, key: StorageKey) -> Union[Object, Directory]:
        ...

    def put(self, object: Object, data: ObjectData) -> None:
        ...

    def remove(self, key: StorageKey) -> None:
        ...

    def list(self, prefix: DirectoryPath, recursive: bool = False) -> List[ObjectPath]:
        ...

    def exists(self, key: StorageKey) -> bool:
        try:
            self.stat(key)
            return True
        except Exception:
            return False

    @property
    def medium(self) -> Medium:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.repository.name}({self.repository.uuid})"

    @property
    def name(self) -> StorageClientKey:
        return StorageClientKey(repr(self))

    # OPTIONAL:
    def get_multiple(self, *keys: ObjectPath) -> List[ObjectData]:
        ...

    def stat_multiple(self, *keys: ObjectPath) -> List[Object]:
        ...

    def put_multiple(self, *objects: Object) -> List[bool]:
        ...

    def remove_multiple(self, *keys: ObjectPath) -> List[bool]:
        ...

    def exists_multiple(self, *keys: ObjectPath) -> List[bool]:
        ...

    # def object_from_bytes(self, key: str, raw: bytes) -> Object:
    #     name = ObjectPath(self, key)
    #     data = ObjectData(__root__=raw)
    #     content = ObjectContentInfo.from_data(data)
    #     return Object(name=name, content=content)

    # MISCELLANEOUS:

    # Hash for ObjectStash client management set replacement
    def __hash__(self):
        return hash(self.name)
