"""Object model for the database service."""
import json
import pickle
from typing import Any, Dict, List, Optional, Set

from jsonmerge import merge
from pydantic import BaseModel, Extra, Json, create_model

MERGE_STRATEGIES = ["overwrite", "discard", "append", "arrayMergeById", "arrayMergeByIndex", "objectMerge", "version"]


class JSON(BaseModel):
    """
    JSON object model for database services. Takes in fields and values with ability to generate JSON schema.
    Allows merging capabilities with other JSON objects assuming valid schema, or schema input at merge-time.
    This includes merging of extra fields, which are not defined in the schema.

    The schema required per-field in 'properties' is:
    "mergeStrategy": "overwrite" | "discard" | "append" | "arrayMergeById" | \
        "arrayMergeByIndex" | "objectMerge" | "version"

    The default merge strategy is 'overwrite'.

    The schema can be generated from the model using the 'schema' method, extra fields not included. Recommended to use
    the generated schema as a base for the final schema, and add the extra fields to the 'properties' field.

    This should be subclassed by the user for their own database models...

    Merging options can be defined for a field like so:
    ```new_field: str = Field("", mergeStrategy="overwrite")```

    Finally, 'parse_obj' method can be used to construct from dictionary while 'from_json' can be used to construct from
    a JSON string.

    Additional information can be found in; https://pypi.org/project/jsonmerge/
    """

    @classmethod
    def merge(cls, old: "JSON", new: "JSON", schema: Optional["JSON"] = None) -> "JSON":
        """
        Merge two JSON objects with a given schema. The schema is used to determine how to merge the objects.
        Precedence of schema overwrite is as follows:
        1. Schema passed to merge method
        2. Schema generated from head object
        3. Schema generated from base object
        """
        if not schema:
            schema = JSON.parse_obj({})
        properties = schema.dict().get("properties", {})

        # Check missing merge strategies in schema for extra fields
        extra_fields = old.extra_fields | new.extra_fields
        if extra_fields:
            missing: List[str] = []
            for field in extra_fields:
                strategy = properties.get(field, {}).get("mergeStrategy", "")
                if strategy not in MERGE_STRATEGIES:
                    missing.append(field)
            if missing:
                raise ValueError(f"Missing 'mergeStrategy' for extra fields: {missing}")

        # Merge provided schemas
        old_schema = old.schema()
        new_schema = new.schema()
        merged_schema = merge(old_schema, new_schema)
        filled_schema = merge(merged_schema, schema.dict())

        # Merge and fill out schema in new object
        result = merge(old.dict(), new.dict(), filled_schema)
        # https://docs.pydantic.dev/usage/models/#dynamic-model-creation
        create_model(
            f"Merged({old.__class__.__name__}#{new.__class__.__name__})",
            __config__=cls.__config__,
            __base__=(type(new), type(old)),
        )

        return cls(**result)

    # Just in case
    class Config:
        extra: Extra = Extra.allow

        @staticmethod
        def schema_extra(schema: Dict[str, Any], _model: type["JSON"]) -> None:
            for prop in schema.get("properties", {}).values():
                if "mergeStrategy" not in prop:
                    prop["mergeStrategy"] = "overwrite"

    @property
    def extra_fields(self) -> Set[str]:
        return set(self.__dict__) - set(self.__fields__)

    @classmethod
    def from_json(cls, json_string: Json) -> "JSON":
        data = json.loads(json_string)
        return cls(**data)

    def to_bytes(self) -> bytes:
        return pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    base = JSON.parse_obj({"a": 1, "b": 2})
    head = JSON.from_json(json.dumps({"a": 3, "c": 4}))
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
