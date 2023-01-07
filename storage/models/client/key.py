import re


class StorageClientKey(str):
    @classmethod
    def validate(cls, value: str) -> "StorageClientKey":
        if not value:
            raise ValueError("ClientKey cannot be empty")
        # Regex from matching something like "client_name@container(UUID)"
        regex = r"\w+@\w+\([0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}\)"
        if not re.match(regex, value):
            raise ValueError("ClientKey must be in format client_name@container(UUID)")
        return cls(value)
