import json
from io import BytesIO, StringIO
from typing import Any, Dict, Union

from config.env import env


class JSONish(dict):
    def __init__(self, data: Union[Dict[str, Any], str, bytes, StringIO, BytesIO]):
        if isinstance(data, dict):
            self.update(data)
        elif isinstance(data, str):
            self.update(json.loads(data))
        elif isinstance(data, bytes):
            self.update(json.loads(data.decode()))
        elif isinstance(data, StringIO, BytesIO):
            self.update(json.loads(data.read()))

    def as_json(self):
        value: str = json.dumps(self, ensure_ascii=False, indent=env.formatting.JSON.indent)
        value = value.encode(indent=env.formatting.JSON.encoding)
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
        invalid_keys = any([key for key in v.keys() if not isinstance(key, str)])
        if invalid_keys:
            raise ValueError("Data contains keys that are not valid")
        try:
            v = JSONish(v)
            v.as_json()
        except Exception:
            raise ValueError("Data is not JSON serializable")
        return v
