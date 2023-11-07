"""StorageClientKey model."""
import re

from pydantic import BaseModel

CLIENT_REGEX = re.compile(
    (
        r"^(?P<client>\w+)@"
        # r"(?P<container>\w+)"
        r"(?P<uuid>[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12})$"
    )
)


class StorageClientKey(BaseModel):
    value: str

    @classmethod
    def validate(cls, value: "StorageClientKey") -> "StorageClientKey":
        if not value:
            raise ValueError("ClientKey cannot be empty")
        # Regex from matching something like "client_type@UUID"
        if not re.match(CLIENT_REGEX, value.value):
            raise ValueError("ClientKey must be in format client_type@UUID")
        return value

    def _get_match(self) -> dict:
        match = re.match(CLIENT_REGEX, self.value)
        if not match:
            raise ValueError("ClientKey must be in format client_type@UUID")
        return match.groupdict()

    @property
    def client(self) -> str:
        return self._get_match()["client"]

    # @property
    # def container(self) -> str:
    #     return self._get_match()["container"]

    @property
    def uuid(self) -> str:
        return self._get_match()["uuid"]
