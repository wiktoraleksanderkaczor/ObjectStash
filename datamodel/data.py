"""Base data model for anything that needs to be JSON serializable"""
import json
from importlib import import_module
from typing import (
    Any,
    Dict,
    Generator,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
import jsonpickle.ext.pandas as jsonpickle_pandas
from jsonmerge import merge as jmerge
from pydantic import BaseModel, Extra

from config.env import env
from config.logger import log
from config.models.env import SerializationFallback

jsonpickle_numpy.register_handlers()
jsonpickle_pandas.register_handlers()

FieldKey = Union[str, int]
FieldPath = List[FieldKey]

MERGE_STRATEGIES = ["overwrite", "discard", "append", "arrayMergeById", "arrayMergeByIndex", "objectMerge", "version"]


def pioneer_json_encoder(v: Any) -> str:
    """Custom JSON encoder (+decoder check) for Pioneer objects."""
    if isinstance(v, BaseModel):
        return v.json()
    has_custom_encoder = getattr(v, "json", None)
    has_custom_decoder = getattr(v, "from_json", None)
    if has_custom_encoder and has_custom_decoder:
        path: str
        try:
            path = f"{v.__class__.__module__}.{v.__class__.__qualname__}"
            # README: Check for absolute path imports later... maybe even from StorageClient
            # path = inspect.getfile(v.__class__) + "." + v.__class__.__name__
        except (TypeError, OSError) as e:
            raise TypeError("Object is not an instance of a JSON serializable class") from e
        encoded = {"__type__": v.__class__.__name__, "__path__": path, "__value__": v.json()}
        return json.dumps(encoded)
    if env.serialization.fallback:
        match env.serialization.fallback:
            case SerializationFallback.JSONPICKLE:
                return str(jsonpickle.encode(v))

    raise TypeError(f"Object of type {v.__class__.__name__} is not JSON serializable")


def pioneer_json_decoder(obj: Dict[str, Any]) -> Any:
    if "__type__" in obj:
        mod = import_module(obj["__path__"])
        cls = getattr(mod, obj["__type__"])
        instance = cls.from_json(obj["__value__"])
        return instance
    if "py/object" in obj and env.serialization.fallback == SerializationFallback.JSONPICKLE:
        return jsonpickle.decode(json.dumps(obj))
    return obj


def pioneer_loads_json(__obj: Union[bytes, bytearray, memoryview, str]) -> Any:
    """Custom JSON decoder for Pioneer objects."""
    return json.loads(__obj, object_hook=pioneer_json_decoder)


def pioneer_dumps_json(__obj: Any, **_: Any) -> str:
    """Custom JSON encoder for Pioneer objects."""
    return json.dumps(__obj, default=pioneer_json_encoder)


class JSON(BaseModel):
    """
    JSON object model for Pioneer services. Made to be subclassed by the user or within the library for their
    own data models. All fields must be JSON serializable. 'parse_obj' can be used to construct from dictionary
    while 'parse_raw' can be used for a JSON bytes/string.

    This is a subclass of Pydantic's BaseModel and allows defining custom JSON encoders and decoders for Python objects.
    Anything that implements a `json` method and a `from_json` classmethod will be serialized and deserialized using
    those methods. The rest will be serialized using the default JSON encoder, followed by the fallback method (if set).
    The 'json' method should return a normal JSON Encoder serializable object and 'from_json' should expect the same
    object as input while returning an instance of the class. This also ensures all keys are strings to satisfy the
    JSON specification. Nested keys are handled by Pydantic.

    Allows merging capabilities with other JSON objects assuming valid schema, or schema input at merge-time.
    Made to be subclassed by the user for their own database models. This includes merging of extra fields, which are
    not defined in the schema. All fields must be JSON serializable.

    The schema can be generated (sans extra fields) from the model using the 'schema' method. Use generated
    base schema and add the extra fields to the 'properties' section.

    The schema required per-field (default being 'overwrite') in 'properties' is:
    `"mergeStrategy": "overwrite" | "discard" | "append" | "arrayMergeById" | \
        "arrayMergeByIndex" | "objectMerge" | "version"`

    Merging options can be defined for a field like so:
    `new_field: str = Field(..., mergeStrategy="overwrite")`

    Additional information can be found in; https://pypi.org/project/jsonmerge/
    """

    @classmethod
    def merge(cls, old: "JSON", new: "JSON", schema: Optional["JSON"] = None) -> Tuple["JSON", "JSON"]:
        """
        A class method that merges two JSON objects with a given schema.

        The schema is used to determine how to merge the objects. The precedence of schema overwrite is as follows:

        1. Schema passed to merge method.
        2. Schema generated from head object.
        3. Schema generated from base object.

        If no schema is provided for a particular field, the default merge strategy is 'overwrite'.

        The method returns the updated schema and merged data objects as instances of the class.

        Args:
            old (JSON): A JSON object representing the original data.
            new (JSON): A JSON object representing the new data.
            schema (Optional[JSON]): A JSON object representing the schema for the data.

        Returns:
            schema (JSON): A JSON object containing the updated schema
            item (JSON): A JSON object containing the merged JSON object data
        """
        if not schema:
            schema = JSON.parse_obj({})
        properties = schema.dict().get("properties", {})

        # Check missing merge strategies in schema for extra fields
        extra_fields = old.extra_fields | new.extra_fields
        extra_strategies = {field: properties.get(field, {}).get("mergeStrategy", "") for field in extra_fields}
        missing_strategies = [field for field, strategy in extra_strategies.items() if strategy not in MERGE_STRATEGIES]
        if missing_strategies:
            log.warning(
                "Missing or wrong 'mergeStrategy' for extra fields, 'overwrite' will be used: %s", missing_strategies
            )

        # Merge provided schemas
        old_schema = old.schema()
        new_schema = new.schema()
        merged_schema = jmerge(old_schema, new_schema)
        filled_schema = jmerge(merged_schema, schema.dict())

        # Merge and fill out schema in new object
        result = jmerge(old.dict(), new.dict(), filled_schema)
        return cls(**filled_schema), cls(**result)

    def get(self, path: FieldPath) -> Any:
        """
        A method that gets a value from the JSON object using a field path.

        Args:
            path (FieldPath): A field path to the value.

        Returns:
            Any: The value at the field path.
        """
        first = str(path.pop(0))
        result: Any = self.dict().get(first)
        for item in path:
            if isinstance(item, int) and isinstance(result, Iterable):
                result = list(result)[item]
            elif isinstance(item, str) and isinstance(result, Mapping):
                result = result.get(item)
            else:
                raise ValueError(f"Invalid field path: {path}")
        return result

    # Implement setting value at arbitrary field path, including within iterables
    def put(self, path: FieldPath, value: Any, create: bool = True) -> None:
        """
        A method that sets a value in the JSON object using a field path.
        Optionally creates the field path if it does not exist.

        Args:
            path (FieldPath): A field path to the value.
            value (Any): The value to set at the field path.
            create (bool): Whether to create the field path if it does not exist.
        """
        if len(path) < 1 or not isinstance(path[0], str):
            raise ValueError(f"Invalid field path: {path}")

        # Group into pairs of keys
        paired: List[Union[FieldKey, None]] = list(path)
        if len(paired) % 2 != 0:
            paired.append(None)
        pairs = zip(paired[::2], paired[1::2])

        item: Any = self
        for k, n in pairs:
            # Default of new object:
            next_item = None
            if isinstance(n, str):
                next_item = {}
            elif isinstance(n, int):
                next_item = []
            else:
                raise ValueError(f"Invalid field path: {path}")

            # If key already exists
            if isinstance(k, str) and isinstance(item, Mapping):
                if k in item:
                    item = dict(item)[k]
                    continue
                if create:
                    setattr(item, k, next_item)
                    item = item[k]
                    continue
                raise ValueError(f"Invalid field path: {path}")

            if isinstance(k, int) and isinstance(item, Iterable):
                # If key in list
                item = list(item)
                if k in range(len(item)):
                    item = item[k]
                    continue
                if create:
                    item.insert(k, next_item)
                    item = item[k]
                    continue
                raise ValueError(f"Invalid field path: {path}")

            # If item does not exist
            raise ValueError(f"Invalid field path: {path}")

        # Set the value at the end of the path
        item = value

    def update(self, value: "JSON") -> None:
        """
        A method that updates the data object with another data object. Matching nested fields by default.

        Args:
            value (JSON): The JSON object to update with.
        """
        for k, v in value.flatten():
            self.put(k, v)

    def flatten(self) -> List[Tuple[FieldPath, Any]]:
        """
        A method that flattens the data object into a list of tuples containing the field path and value.

        Returns:
            List[Tuple[FieldPath, Any]]: A list of tuples containing the field path and value.
        """

        def flattened(path: FieldPath, val: Any) -> Generator[Tuple[FieldPath, Any], None, None]:
            if isinstance(val, Mapping):
                for k, v in val.items():
                    yield from flattened(path + [k], v)
            elif isinstance(val, Iterable):
                for i, v in enumerate(val):
                    yield from flattened(path + [i], v)
            else:
                yield (path, val)

        return list(flattened([], self.dict()))

    @classmethod
    def inflate(cls, flat: List[Tuple[FieldPath, Any]]) -> "JSON":
        """
        A method that updates the data object with a list of tuples containing the field path and value.

        Args:
            flat (List[Tuple[FieldPath, Any]]): A list of tuples containing the field path and value.
        """
        data = cls()
        for path, value in flat:
            data.put(path, value)
        return data

    # Just in case
    class Config:
        extra: Extra = Extra.allow
        json_dumps = pioneer_dumps_json
        json_loads = pioneer_loads_json

        @staticmethod
        def schema_extra(schema: Dict[str, Any], _model: type["JSON"]) -> None:
            schema["description"] = "Data model for database service"  # _model.__doc__
            for prop in schema.get("properties", {}).values():
                if "mergeStrategy" not in prop:
                    prop["mergeStrategy"] = "overwrite"

    @property
    def extra_fields(self) -> Set[str]:
        return set(self.__dict__) - set(self.__fields__)


if __name__ == "__main__":
    base = JSON.parse_obj({"a": 1, "b": 2})
    head = JSON.parse_raw(json.dumps({"a": 3, "c": 4}))
    print(base)
    print(head)
    print(base.dict())
    print(base.json())
    print(base.schema())
    print(head.schema())
    merge_schema = {
        "properties": {
            "a": {"mergeStrategy": "overwrite"},
            "b": {"mergeStrategy": "overwrite"},
            "c": {"mergeStrategy": "overwrite"},
        }
    }
    _schema, merged = JSON.merge(base, head, JSON.parse_obj(merge_schema))
    print(merged)
    print(merged.flatten())
