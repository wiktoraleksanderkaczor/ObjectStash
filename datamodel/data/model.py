"""
Base data model for anything that needs to be data object serializable and mergeable.
Also includes a change tracker for tracking changes to immutable data objects.
"""
import json
from collections.abc import MutableMapping, MutableSequence, MutableSet
from enum import Enum
from importlib import import_module
from typing import (
    Any,
    Dict,
    Generator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
import jsonpickle.ext.pandas as jsonpickle_pandas
from jsonmerge import merge as jmerge
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

from datamodel.data.changes import ChangeTracker
from datamodel.data.path import FieldKey, FieldPath
from datamodel.data.protocol.data import DataProtocol
from datamodel.data.view.flattened import FlatData
from datamodel.data.view.nested import NestedData

jsonpickle_numpy.register_handlers()
jsonpickle_pandas.register_handlers()


class MergeType(str, Enum):
    OVERWRITE = "overwrite"
    DISCARD = "discard"
    APPEND = "append"
    ARRAY_MERGE_BY_ID = "arrayMergeById"
    ARRAY_MERGE_BY_INDEX = "arrayMergeByIndex"
    OBJECT_MERGE = "objectMerge"
    VERSION = "version"


def custom_json_encoder(v: Any) -> str:
    """Custom encoder for internal objects."""
    if isinstance(v, BaseModel):
        return v.model_dump_json()
    if isinstance(v, DataProtocol):
        path: str
        try:
            path = f"{v.__class__.__module__}.{v.__class__.__qualname__}"
            # README: Check for absolute path imports later... maybe even from StorageClient
            # path = inspect.getfile(v.__class__) + "." + v.__class__.__name__
        except (TypeError, OSError) as e:
            raise TypeError("Object is not an instance of a serializable class") from e
        encoded = {"__type__": v.__class__.__name__, "__path__": path, "__value__": v.to_data().to_json()}
        return json.dumps(encoded)
    try:
        return str(jsonpickle.encode(v))
    except Exception as e:
        raise TypeError(f"Object of type {v.__class__.__name__} is not JSON serializable") from e


def custom_json_decoder(obj: Dict[str, Any]) -> Any:
    """Custom decoder for internal objects."""
    if "__type__" in obj:
        mod = import_module(obj["__path__"])
        cls = getattr(mod, obj["__type__"])
        if not isinstance(cls, DataProtocol):
            raise TypeError(f"Object of type {cls.__name__} is not deserializable")
        instance = cls.from_data(obj["__value__"])
        return instance
    if "py/object" in obj:
        return jsonpickle.decode(json.dumps(obj))
    return obj


def custom_loads_json(__obj: Union[bytes, bytearray, memoryview, str]) -> Any:
    """Custom JSON decoder for Pioneer objects."""
    return json.loads(__obj, object_hook=custom_json_decoder)


def custom_dumps_json(__obj: Any, **_: Any) -> str:
    """Custom JSON encoder for Pioneer objects."""
    return json.dumps(__obj, default=custom_json_encoder)


def custom_json_schema(schema: Dict[str, Any], _: type["Data"]) -> None:
    # schema["description"] = "Data model for database service"  # _model.__doc__
    for prop in schema.get("properties", {}).values():
        if "mergeStrategy" not in prop:
            prop["mergeStrategy"] = MergeType.OVERWRITE


class Data(BaseModel):
    """
    Data object model for internal services, made to be subclassed.
    All origin keys must be strings per JSON specification.
    All fields must be serializable with the data protocol, falls back to 'jsonpickle'.

    Allows merging capabilities with other data objects assuming valid schema, or schema input at merge-time.
    This includes merging of extra fields, which are not defined in the schema.

    The schema can be generated (sans extra fields) from the model using the 'schema' method. Use generated
    base schema and add the extra fields to the 'properties' section.

    The schema required per-field (default being 'overwrite') in 'properties' is:
    `"mergeStrategy": "overwrite" | "discard" | "append" | "arrayMergeById" | \
        "arrayMergeByIndex" | "objectMerge" | "version"`

    Merging options can be defined for a field like so:
    `new_field: str = Field(..., json_schema_extra={"mergeStrategy": "overwrite"})`

    Additional information can be found in; https://pypi.org/project/jsonmerge/
    """

    model_config: ConfigDict = ConfigDict(
        extra="allow", validate_assignment=True, json_schema_extra=custom_json_schema, arbitrary_types_allowed=True
    )
    model_json_dumps = custom_dumps_json
    model_json_loads = custom_loads_json

    def __init__(self, *args, **data: Any) -> None:
        super().__init__(*args, **data)
        self._changes: ChangeTracker = ChangeTracker()

    @classmethod
    def merge(cls, old: "Data", new: "Data", schema: Optional["Data"] = None) -> Tuple["Data", "Data"]:
        """
        A class method that merges two data objects with a given schema.

        The schema is used to determine how to merge the objects. The precedence of schema overwrite is as follows:

        1. Schema passed to merge method.
        2. Schema generated from head object.
        3. Schema generated from base object.

        If no schema is provided for a particular field, the default merge strategy is 'overwrite'.

        The method returns the updated schema and merged data objects as instances of the class.

        Args:
            old (Data): A data object representing the original data.
            new (Data): A data object representing the new data.
            schema (Optional[Data]): A data object representing the schema for the data.

        Returns:
            schema (Data): A data object containing the updated schema
            item (Data): A data object containing the merged data object data
        """
        # Generate schema if not provided
        if not isinstance(schema, Data):
            schema = Data()

        # Merge provided schemas
        old_schema = old.model_json_schema()
        new_schema = new.model_json_schema()
        merged_schema = jmerge(old_schema, new_schema)
        filled_schema = jmerge(merged_schema, schema.to_dict())

        # Merge and fill out schema in new object
        result = jmerge(old.to_dict(), new.to_dict(), filled_schema)
        return cls(**filled_schema), cls(**result)

    def _is_valid_path(self, path: FieldPath) -> bool:
        """A method that checks whether a field path is valid.
        TODO: Reimplement to not use 'to_dict' method."""
        if len(path) < 1 or not isinstance(path[0], str):
            return False

        root = self.to_dict()
        valid = []
        for item in path[:-1]:
            if not isinstance(item, (str, int)):
                return False
            if isinstance(item, str) and isinstance(root, Mapping):
                root = root[item]
            elif isinstance(item, int) and isinstance(root, Sequence):
                root = root[item]
            else:
                return False
            valid.append(item)

        return True

    def get(self, path: FieldPath, default: Any = None) -> Any:
        """
        A method that gets a value from the data object using a field path.

        Args:
            path (FieldPath): A field path to the value.
            default (Any): A default value to return if the field path does not exist.

        Returns:
            Any: The value at the field path.
        """
        try:
            return self[path]
        except KeyError:
            return default

    def __getitem__(self, path: FieldPath) -> Any:
        """
        A method that gets a value from the data object using a field path.

        Args:
            path (FieldPath): A field path to the value.

        Returns:
            Any: The value at the field path.
        """
        # if not self._is_valid_path(path):
        if not isinstance(path[0], str):
            raise ValueError(f"Invalid field path: {path}")

        # Check for changes
        if path in self._changes:
            return self._changes[path]

        # Check for changes in parents
        for length in reversed(range(len(path))):
            if path[:length] in self._changes:
                return self._changes[path[:length]]

        for item in reversed(path):
            return self._changes[path]

        root = getattr(self, path[0], None)
        if root is None:
            raise KeyError(f"'{path[0]}' not found in model")

        for item in path[1:]:
            if isinstance(item, int) and isinstance(root, Sequence):
                root = root[item]
            elif isinstance(item, str) and isinstance(root, Mapping):
                root = root.get(item)
        return root

    # Implement setting value at arbitrary field path, including within iterables
    def __setitem__(self, path: FieldPath, value: Any) -> None:
        """
        A method that sets a value in the data object using a field path.
        Optionally creates the field path if it does not exist.

        Args:
            path (Sequence[FieldKey]): A field path to the value.
            value (Any): The value to set at the field path.
            create (bool): Whether to create the field path if it does not exist.
        """
        if not isinstance(path[0], str):
            raise ValueError(f"Invalid field path: {path}")

        is_valid = self._is_valid_path(path)
        if not is_valid:
            raise ValueError(f"Invalid field path: {path}")

        self._changes[path] = value

    def __contains__(self, path: FieldPath) -> bool:
        value = self.get(path, None)
        if not value:
            return False
        return True

    def update(self, value: "Data") -> None:
        """
        A method that updates the data object with another data object. Matching nested fields by default.

        Args:
            value (Data): Object for update data.
        """
        for k, v in value.flattened:
            self._changes[k] = v

    @classmethod
    def inflate(cls, flattened: FlatData) -> Self:
        """
        A method that updates the data object with a list of tuples with mapping of field path to value.

        Args:
            flat (List[Tuple[FieldPath, Any]]): A list of tuples with mapping of field path to value.
        """
        # Sort by length of path, ascending
        ordered = sorted(flattened, key=lambda x: len(x[0]))

        # Convert to dict by prefix
        model = {}
        for path, value in ordered:
            prefix = model
            for idx, part in enumerate(path, start=1):
                # If exists, set prefix
                if part in prefix:
                    prefix = prefix[part]
                    continue

                # If end of path, set value
                if idx == len(path):
                    prefix[part] = value
                    break

                # If next part is int, set prefix to list
                if isinstance(path[idx], int):
                    prefix[part] = []
                # If next part is str, set prefix to dict
                elif isinstance(path[idx], str):
                    prefix[part] = {}
                prefix = prefix[part]

        return cls.from_obj(model)

    @classmethod
    def from_obj(cls, __obj: Any) -> Self:
        """Construct a data object from a Python object i.e. dictionary"""
        return cls.model_validate(__obj)

    @classmethod
    def from_raw(cls, __obj: Union[bytes, bytearray, memoryview, str]) -> Self:
        """Construct a data object from a raw JSON string or binary data."""
        return cls.model_validate_json(__obj)

    def build(self) -> "Data":
        """Builds the data object."""
        # If no changes, return model dump
        if not self._changes:
            return self

        # Data with applied changes
        return self._changes.apply(self)

    def to_json(self) -> str:
        """Converts the object to a JSON-compatible representation."""
        return self.build().model_dump_json()

    def to_dict(self) -> Dict[str, Any]:
        """Converts the object to a dictionary."""
        return self.build().model_dump()

    def to_json_schema(self) -> Dict[str, Any]:
        """Returns the schema for the object."""
        if not self._changes:
            return self.model_json_schema()
        update = self.from_obj(self.to_dict())
        return update.model_json_schema()

    @property
    def model_extra(self) -> Dict[str, Any]:
        model_extra = {}
        if isinstance(self.model_extra, dict):
            model_extra = self.model_extra
        return model_extra

    @property
    def model_extra_set(self) -> Set[str]:
        return set(self.model_extra.keys())

    @property
    def changes(self) -> ChangeTracker:
        return self._changes

    def keys(self) -> Generator[FieldPath, None, None]:
        for path, _ in self.flattened:
            yield path

    def values(self) -> Generator[Any, None, None]:
        for _, value in self.flattened:
            yield value

    def items(self) -> Generator[Tuple[FieldPath, Any], None, None]:
        for path, value in self.flattened:
            yield path, value

    @property
    def flattened(self) -> FlatData:
        """
        A method that flattens the data object into a list of tuples with mapping of field path to value.

        Returns:
            List[Tuple[FieldPath, Any]]: A list of tuples with mapping of field path to value.
        """

        def _flattened(path: FieldPath, val: Any) -> List[Tuple[FieldPath, Any]]:
            paths = []

            if isinstance(val, MutableMapping):
                for k, v in val.items():
                    key = k if isinstance(k, FieldKey) else repr(k)
                    paths.extend(_flattened((*path, key), v))
            elif isinstance(val, Mapping):
                paths.append((path, val))

            elif isinstance(val, MutableSet):
                for v in val:
                    paths.extend(_flattened(path, v))
            elif isinstance(val, Set):
                paths.append((path, val))

            elif isinstance(val, MutableSequence):
                for i, v in enumerate(val):
                    paths.extend(_flattened((*path, str(i)), v))
            elif isinstance(val, Sequence):
                paths.append((path, val))

            else:
                paths.append((path, val))

            return paths

        return FlatData(_flattened([], self.to_dict()))

    @property
    def nested(self) -> NestedData:
        data = {}
        for path, value in self.flattened:
            root = data
            for part in path[:-1]:
                if part not in root:
                    root[part] = {}
                root = root[part]
            root[path[-1]] = value
        return NestedData(data)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Data):
            return False
        return self.to_dict() == other.to_dict()

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.build().to_dict()})"

    def __str__(self) -> str:
        return repr(self)


if __name__ == "__main__":
    obj1 = Data.from_obj({"a": 1, "b": 2, "3": "c"})
    obj2 = Data.from_raw(json.dumps({"a": 3, "c": 4}))

    obj1_dict = obj1.to_dict()
    obj2_dict = obj2.to_dict()

    obj1_schema = obj1.to_json_schema()
    obj2_schema = obj2.to_json_schema()

    merge_schema = {
        "properties": {
            "a": {"mergeStrategy": "overwrite"},
            "b": {"mergeStrategy": "overwrite"},
            "c": {"mergeStrategy": "overwrite"},
        }
    }
    merge_schema, merge = Data.merge(obj1, obj2, Data.from_obj(merge_schema))

    print(merge)
    print(merge.flattened)
    print(merge_schema)
    print(merge_schema.flattened)

    referencial = Data.from_obj({"a": 1, "b": 2, "c": {"d": [5, 1, 2, 3], "e": 4}})
    # *path: FieldKey
    # referencial["c", "d", 2] = 5

    print(referencial)
    print(referencial.build())

    referencial[["c", "d", 2]] = 5

    print(referencial)
    print(referencial.build())

    print(referencial.nested)

    class SomeRandom(Data):
        rando: int = Field(..., json_schema_extra={"mergeStrategy": "discard"})

    random1 = SomeRandom.from_obj({"rando": 1})
    random2 = SomeRandom.from_obj({"rando": 2, "2": 2})
    random1.update(random2)
    dumped = random1.model_dump()
    print(random1)
    print(random1.to_json_schema())
    print(random1.flattened)
    print(random1.to_dict())
    print(random1.to_json())
