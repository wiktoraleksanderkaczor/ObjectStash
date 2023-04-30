"""Object model for the database service."""
import json
from typing import Any, Dict, Generator, Iterable, List, Mapping, Optional, Tuple, Union

from jsonmerge import merge

from config.logger import log
from database.models.client import FieldKey, FieldPath
from datamodel.data import PioneerBaseModel

MERGE_STRATEGIES = ["overwrite", "discard", "append", "arrayMergeById", "arrayMergeByIndex", "objectMerge", "version"]


class JSON(PioneerBaseModel):
    """
    JSON object model for database services, extending the PioneerBaseModel. Allows merging capabilities with other
    JSON objects assuming valid schema, or schema input at merge-time. Made to be subclassed by the user for their
    own database models. This includes merging of extra fields, which are not defined in the schema.
    All fields must be JSON serializable.

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

        # Handle setting the root value only
        # if len(path) == 1:
        #     setattr(self, path[0], value)
        #     return

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

    def update(self, value: "JSON", nested: bool = True) -> None:
        """
        A method that updates the JSON object with another JSON object. Matching nested fields by default.

        Args:
            value (JSON): The JSON object to update with.
            nested (bool): Whether to update nested fields.
        """
        if not nested:
            for k, v in value.dict().items():
                self.put([k], v)
        else:
            for k, v in value.flatten():
                self.put(k, v)

    def flatten(self) -> List[Tuple[FieldPath, Any]]:
        """
        A method that flattens the JSON object into a list of tuples containing the field path and value.

        Returns:
            List[Tuple[FieldPath, Any]]: A list of tuples containing the field path and value.
        """

        def flattened(path: FieldPath, val: Any) -> Generator[Tuple[FieldPath, Any], None, None]:
            if isinstance(val, Mapping):
                for k, v in val.items():
                    yield from flattened(path + k, v)
            elif isinstance(val, Iterable):
                for i, v in enumerate(val):
                    yield from flattened(path + [i], v)
            else:
                yield (path, val)

        return list(flattened([], self.dict()))

    @classmethod
    def from_flattened(cls, flat: List[Tuple[FieldPath, Any]]) -> "JSON":
        """
        A method that updates the JSON object with a list of tuples containing the field path and value.

        Args:
            flat (List[Tuple[FieldPath, Any]]): A list of tuples containing the field path and value.
        """
        data = cls()
        for path, value in flat:
            data.put(path, value)
        return data

    # Just in case
    class Config(PioneerBaseModel.Config):
        @staticmethod
        def schema_extra(schema: Dict[str, Any], _model: type["JSON"]) -> None:
            schema["description"] = "Data model for database service"  # _model.__doc__
            for prop in schema.get("properties", {}).values():
                if "mergeStrategy" not in prop:
                    prop["mergeStrategy"] = "overwrite"


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
