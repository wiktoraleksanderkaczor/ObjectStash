"""Object model for the database service."""
import json
from importlib import import_module
from typing import Any, Dict, Optional, Set, Tuple, Union

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
import jsonpickle.ext.pandas as jsonpickle_pandas
from jsonmerge import merge
from pydantic import BaseModel, Extra

from config.env import env
from config.logger import log
from config.models.env import DatabaseFallback

jsonpickle_numpy.register_handlers()
jsonpickle_pandas.register_handlers()

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
    if env.database.fallback:
        match env.database.fallback:
            case DatabaseFallback.JSONPICKLE:
                return str(jsonpickle.encode(v))

    raise TypeError(f"Object of type {v.__class__.__name__} is not JSON serializable")


def pioneer_json_decoder(obj: Dict[str, Any]) -> Any:
    if "__type__" in obj:
        mod = import_module(obj["__path__"])
        cls = getattr(mod, obj["__type__"])
        instance = cls.from_json(obj["__value__"])
        return instance
    if "py/object" in obj and env.database.fallback == DatabaseFallback.JSONPICKLE:
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
    JSON object model for database services. Takes in fields and values with ability to generate JSON schema.
    Allows merging capabilities with other JSON objects assuming valid schema, or schema input at merge-time.
    Made to be subclassed by the user for their own database models. This includes merging of extra fields, which
    are not defined in the schema. All fields must be JSON serializable.

    The schema can be generated (sans extra fields) from the model using the 'schema' method. Use generated
    base schema and add the extra fields to the 'properties' section.

    'parse_obj' can be used to construct from dictionary while 'parse_raw' can be used for a JSON bytes/string.

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

        The method returns the updated schema and merged JSON objects as instances of the class.

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
        merged_schema = merge(old_schema, new_schema)
        filled_schema = merge(merged_schema, schema.dict())

        # Merge and fill out schema in new object
        result = merge(old.dict(), new.dict(), filled_schema)
        return cls(**filled_schema), cls(**result)

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
    print(JSON.merge(base, head, JSON.parse_obj(merge_schema)))
