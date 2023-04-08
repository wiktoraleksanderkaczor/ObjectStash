"""Database configuration model."""
from typing import Dict, List, Union

from compute.interface.functions.interface import FunctionInterface
from database.models.client import FieldPath
from database.models.objects import JSON


class DatabaseConfig(JSON):
    calculated: Dict[Union[FieldPath, List[FieldPath]], FunctionInterface]
