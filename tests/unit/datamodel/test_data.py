"""
Test the JSON data structure in the data models
"""
import pytest

from datamodel.data.model import Data


@pytest.mark.parametrize(
    "obj1, obj2, result",
    [
        (
            Data(a="1", b="2"),
            Data(c="3", d="4"),
            Data(a="1", b="2", c="3", d="4"),
        ),
        (Data(a="1", b="2"), Data(a="3", b="4", c="3", d="4"), Data(a="3", b="4", c="3", d="4")),
    ],
)
def test_json_merge(obj1, obj2, result):
    _, merged = Data.merge(obj1, obj2)
    assert merged == result
