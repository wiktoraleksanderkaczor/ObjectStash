"""Data model for object data."""

from pydantic import BaseModel, StrictBytes


class FileData(BaseModel):
    __root__: StrictBytes

    def to_text(self) -> str:
        return self.__root__.decode()
