from pathlib import PurePosixPath as CacheID

from pydantic import BaseModel, Extra


# Allow extra for arbitrary kwarg fields, or inner basemodel
class CacheData(BaseModel):
    class Config:
        extra = Extra.allow


class CacheInfo(BaseModel):
    pass


class CacheObject(BaseModel):
    name: CacheID
    info: CacheInfo
    data: CacheData
