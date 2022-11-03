import json

# from collections.abc import Iterable
from io import BytesIO, StringIO
from pathlib import PurePosixPath as Key
from typing import Any, Dict, Union, overload

from models.storage import MergeMode  # , List, Union

from ..utils.env import env

# from .storage import StorageError


# def jsonable_args(ags: Union[List[int], int], kws: Union[List[str], str]):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             try:
#                 # Adjust argument index by minus one
#                 if not isinstance(ags, Iterable):
#                     ags = [ags - 1]
#                 else:
#                     ags = [key - 1 for key in ags]
#                 # Make kws an interable if not already
#                 if not isinstance(kws, Iterable):
#                     kws = [kws]
#                 # Retrieve values to JSONify
#                 ags = [args[key] for key in ags]
#                 kws = {key: kwargs[key] for key in kws}
#                 json.dumps({'args': ags, 'kwargs': kws})
#                 return func(*args, **kwargs)
#             except Exception:
#                 raise StorageError(f'Arguments are not JSON serializable')
#         return wrapper
#     return decorator


class MergeStrategy(dict):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, dict):
            raise TypeError(f"Expected a dictionary, not {type(v)}")
        invalid_keys = any([key for key in v.keys() if not isinstance(key, Key)])
        if invalid_keys:
            raise ValueError("MergeStrategy contains keys that are not valid")
        for val in v.values():
            if isinstance(val, dict):
                MergeStrategy.validate(val)
            elif not isinstance(val, MergeMode):
                raise ValueError("Value is not of type MergeMode")
        return v


class MergeIndex(dict):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, dict):
            raise TypeError(f"Expected a dictionary, not {type(v)}")
        invalid_keys = any([key for key in v.keys() if not isinstance(key, Key)])
        if invalid_keys:
            raise ValueError("MergeIndex contains keys that are not valid")
        for val in v.values():
            if isinstance(val, dict):
                MergeIndex.validate(val)
            elif not isinstance(val, int):
                raise ValueError("Index value is not of integer type")
        return v


class JSONish(dict):
    @overload
    def __init__(self, data: Union[Dict[str, Any], str, StringIO, BytesIO]):
        if isinstance(data, dict):
            self.update(data)
        elif isinstance(data, str):
            self.update(json.loads(data))
        elif isinstance(data, StringIO, BytesIO):
            self.update(json.loads(data.read()))

    def as_json(self):
        value: str = json.dumps(self, ensure_ascii=False, indent=env["DATA"]["JSON"]["INDENT"])
        value = value.encode(env["DATA"]["JSON"]["ENCODING"])
        return value

    def as_dict(self):
        return self

    def as_stringio(self):
        return StringIO(self.as_json())

    def as_bytesio(self):
        return BytesIO(self.as_json())

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, dict):
            pass
        elif isinstance(v, str):
            v = json.loads(v)
        elif isinstance(v, StringIO):
            v = json.load(v)
        else:
            raise TypeError(f"Expected a dictionary, string or StringIO, not {type(v)}")
        invalid_keys = any([key for key in v.keys() if not isinstance(key, Key)])
        if invalid_keys:
            raise ValueError("Data contains keys that are not valid")
        try:
            v = JSONish(v)
            v.as_json()
        except Exception:
            raise ValueError("Data is not JSON serializable")
        return v
