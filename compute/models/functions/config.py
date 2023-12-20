"""Function configuration model."""
from datamodel.data.model import Data
from datamodel.timedate import TimeDelta
from storage.models.client.key import StorageClientKey


class FunctionConfig(Data):
    name: str
    storage: StorageClientKey
    timeout: TimeDelta
    # role: str # README: Add role-based access control and possibly a role model
