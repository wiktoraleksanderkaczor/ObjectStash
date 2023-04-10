"""Database configuration model."""
from typing import Dict

from compute.models.functions.config import FunctionConfig
from database.models.client import FieldPath
from database.models.objects import JSON


class DatabaseConfig(JSON):
    operations: Dict[FieldPath, FunctionConfig]  # README: Calculated fields and constraints
