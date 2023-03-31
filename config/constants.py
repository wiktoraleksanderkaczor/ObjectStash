"""Constants for the configuration."""
import os

CONFIG_PATH = os.environ.get("PIONEER_CONFIG_PATH", ".pioneer.json")
CONFIG_SCHEMA_PATH = os.environ.get("PIONEER_CONFIG_SCHEMA_FNAME", ".pioneer.schema.json")
