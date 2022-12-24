from pydantic import BaseModel, StrictBytes


class ObjectData(BaseModel):
    __root__: StrictBytes
