"""Custom datetime class for use with JSON serialization."""
from datetime import datetime


class DateTime(datetime):
    def json(self):
        return self.isoformat()

    @classmethod
    def from_json(cls, value):
        return datetime.fromisoformat(value)
