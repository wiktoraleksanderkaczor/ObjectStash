"""Data model for object data."""
from pydantic import BaseModel, StrictBytes


class FileData(BaseModel):
    __root__: StrictBytes
