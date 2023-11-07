"""
Test the JSON data structure in the data models
"""
import pytest

from datamodel.data import JSON


@pytest.mark.parametrize(
    "obj1, obj2, result",
    [
        (
            JSON.from_obj({"a": "1", "b": "2"}),
            JSON.from_obj({"c": "3", "d": "4"}),
            JSON.from_obj({"a": "1", "b": "2", "c": "3", "d": "4"}),
        ),
        (
            JSON.from_obj({"a": "1", "b": "2"}),
            JSON.from_obj({"a": "3", "b": "4"}),
            JSON.from_obj({"a": "3", "b": "4"}),
        ),
    ],
)
def test_json_merge(obj1, obj2, result):
    _, merged = JSON.merge(obj1, obj2)
    assert merged == result
