from enum import Enum


class MergeMode(str, Enum):
    UPDATE = "UPDATE"
    ADDITIVE = "ADDITIVE"
    SUBTRACT = "SUBTRACT"
    INTERSECT = "INTERSECT"  # If value in both sides


class MergeStrategy(dict):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, dict):
            raise TypeError(f"Expected a dictionary, not {type(v)}")
        invalid_keys = any([key for key in v.keys() if not isinstance(key, str)])
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
        invalid_keys = any([key for key in v.keys() if not isinstance(key, str)])
        if invalid_keys:
            raise ValueError("MergeIndex contains keys that are not valid")
        for val in v.values():
            if isinstance(val, dict):
                MergeIndex.validate(val)
            elif not isinstance(val, int):
                raise ValueError("Index value is not of integer type")
        return v
