"""Base data model for anything that needs to be JSON serializable"""
import json
from importlib import import_module
from typing import Any, Dict, Set, Union

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
import jsonpickle.ext.pandas as jsonpickle_pandas
from pydantic import BaseModel, Extra

from config.env import env
from config.models.env import SerializationFallback

jsonpickle_numpy.register_handlers()
jsonpickle_pandas.register_handlers()


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


class PioneerBaseModel(BaseModel):
    """
    Pioneer base model for JSON serializable objects. This is a subclass of Pydantic's BaseModel and allows defining
    custom JSON encoders and decoders for Python objects. Anything that implements a `json` method and a `from_json`
    classmethod will be serialized and deserialized using those methods. The rest will be serialized using the default
    JSON encoder, followed by the fallback method (if set). The 'json' method should return a normal JSON Encoder
    serializable object and 'from_json' should expect the same object as input while returning an instance of the class.
    """

    # Just in case
    class Config:
        extra: Extra = Extra.allow
        json_dumps = pioneer_dumps_json
        json_loads = pioneer_loads_json

    @property
    def extra_fields(self) -> Set[str]:
        return set(self.__dict__) - set(self.__fields__)
