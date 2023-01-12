import re

CLIENT_REGEX = re.compile(
    (
        r"^(?P<client>\w+)@"
        r"(?P<container>\w+)"
        r"\((?P<uuid>[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12})\)$"
    )
)


class StorageClientKey(str):
    @classmethod
    def validate(cls, value: str) -> "StorageClientKey":
        if not value:
            raise ValueError("ClientKey cannot be empty")
        # Regex from matching something like "client_name@container(UUID)"
        if not re.match(CLIENT_REGEX, value):
            raise ValueError("ClientKey must be in format client_name@container(UUID)")
        return cls(value)

    def _get_match(self) -> dict:
        match = re.match(CLIENT_REGEX, self)
        if not match:
            raise ValueError("ClientKey must be in format client_name@container(UUID)")
        return match.groupdict()

    @property
    def client(self) -> str:
        return self._get_match()["client"]

    @property
    def container(self) -> str:
        return self._get_match()["container"]

    @property
    def uuid(self) -> str:
        return self._get_match()["uuid"]
