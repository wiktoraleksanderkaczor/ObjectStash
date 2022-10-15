import json
import re
from ast import Bytes
#from collections.abc import Iterable
from datetime import datetime
from io import BytesIO, StringIO
from typing import Any, Dict, Union, overload

from pydantic import BaseModel, validator

from storage import MergeMode  # , List, Union

from .env import env

#from .storage import StorageError


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


def normalize_path(path: str) -> str:
    return path if path.endswith('/') else f'{path}/'


class Key(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError(f'Expected a string, not {type(v)}')
        if '/' in v:
            raise ValueError('Keys must not contain forward-slashes')
        if '.' in v:
            raise ValueError('Keys must not contain dots')
        return v


class MergeStrategy(dict):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, dict):
            raise TypeError(f'Expected a dictionary, not {type(v)}')
        invalid_keys = any(
            [key for key in v.keys() if not isinstance(key, Key)])
        if invalid_keys:
            raise ValueError(f'MergeStrategy contains keys that are not valid')
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
            raise TypeError(f'Expected a dictionary, not {type(v)}')
        invalid_keys = any(
            [key for key in v.keys() if not isinstance(key, Key)])
        if invalid_keys:
            raise ValueError(f'MergeIndex contains keys that are not valid')
        for val in v.values():
            if isinstance(val, dict):
                MergeIndex.validate(val)
            elif not isinstance(val, int):
                raise ValueError("Index value is not of integer type")
        return v


class ISOTimeStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            datetime.fromisoformat(v)
        except Exception:
            raise ValueError(
                'String is not parsable as datetime from ISO format')
        return v


class PrefixPath(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError(f'Expected a string, not {type(v)}')
        if not v.endswith('/'):
            v = f'{v}/'
        return v


class Filename(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError(f'Expected a string, not {type(v)}')
        valid_filename = r'^\w+(\.\w+)+$'
        if not re.match(valid_filename, v):
            raise ValueError(
                f'Filenames is not valid according to "{valid_filename}" regex')
        return v


class ObjectPath(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError(f'Expected a string, not {type(v)}')
        try:
            prefix, fname = v.rsplit("/", 1)
            if not prefix or not fname:
                raise ValueError(
                    f'Could not split "{v}" into prefix and filename')
            prefix = PrefixPath(prefix)
            prefix = prefix.validate()
            fname = Filename(fname)
            fname = fname.validate()
        except ValueError as e:
            raise e
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
        value: str = json.dumps(
            self,
            ensure_ascii=False,
            indent=env['DATA']['JSON']['INDENT'])
        value = value.encode(env['DATA']['JSON']['ENCODING'])
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
            raise TypeError(
                f'Expected a dictionary, string or StringIO, not {type(v)}')
        invalid_keys = any(
            [key for key in v.keys() if not isinstance(key, Key)])
        if invalid_keys:
            raise ValueError(f'Data contains keys that are not valid')
        try:
            v = JSONish(v)
            v.as_json()
        except Exception:
            raise ValueError(f'Data is not JSON serializable')
        return v


class Object(BaseModel):
    key: str

    @validator('key')
    def valid_key(cls, v: str):
        if '.' in v:
            raise ValueError('Key cannot contain dots')
        if v.endswith('/'):
            raise ValueError('Object path cannot end with a forward-slash')
        return v
