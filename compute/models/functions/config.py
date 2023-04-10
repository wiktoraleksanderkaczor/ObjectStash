"""Function configuration model."""
from pydantic import BaseModel

from datamodel.timedate import TimeDelta
from storage.models.client.key import StorageClientKey


class FunctionConfig(BaseModel):
    name: str
    storage: StorageClientKey
    timeout: TimeDelta
    # role: str # README: Add role-based access control and possibly a role model
