"""Object model for the database service."""
import json
import pickle
from typing import Any, Dict, Optional, Set, Tuple

from jsonmerge import merge
from pydantic import BaseModel, Extra, Json

from config.logger import log

MERGE_STRATEGIES = ["overwrite", "discard", "append", "arrayMergeById", "arrayMergeByIndex", "objectMerge", "version"]


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
