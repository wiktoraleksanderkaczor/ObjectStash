from typing import Any, Dict, Union

from jsonmerge import merge
from pydantic import BaseModel, Extra, Json


class JSON(BaseModel):
    # Should I use str or StrictStr? The latter prevents coercion from other types, like int one being string one
    __root__: Union[Json, Dict[str, Any]]

    @classmethod
    def merge(cls, base: "JSON", head: "JSON") -> "JSON":
        result = merge(base.dict(), head.dict(), head.schema())
        return cls(__root__=result)

    # Just in case
    class Config:
        extra: Extra = Extra.allow

        # Default values for all fields, work out passing parameters later
        @staticmethod
        def schema_extra(schema: dict[str, Any], model: type["JSON"]) -> None:
            for prop in schema.get("properties", {}).values():
                # prop.pop("title", None)
                prop["mergeStrategy"] = "overwrite"
