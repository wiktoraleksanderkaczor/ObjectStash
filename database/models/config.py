"""Database configuration model."""
from typing import Dict

from compute.models.functions.config import FunctionConfig
from database.models.client import FieldPath
from database.models.objects import JSON


class DatabaseConfig(JSON):
    operations: Dict[FieldPath, FunctionConfig]  # Calculated fields
    # triggers: Dict[FieldPath, str]  # Triggers
    # constraints: Dict[FieldPath, str]  # Constraints
    # foreign: Dict[FieldPath, str]  # Foreign keys
    # views: Dict[FieldPath, str]  # Views
    # triggers: Dict[FieldPath, str]  # Triggers
    # logging: Dict[FieldPath, str]  # Logging
