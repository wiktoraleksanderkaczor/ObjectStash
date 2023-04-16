"""Field path specification model for the database service.

Given the following data, extracting the first name of the first person in the list of names yields:
{"name": [{"first": "John", "last": "Doe"}, {"first": "Jane", "last": "Doe"}]} -> ["name", 0, "first"] -> "John"
"""
from typing import List, Union

FieldPath = List[Union[str, int]]
