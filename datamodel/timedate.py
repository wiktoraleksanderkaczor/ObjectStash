"""Custom datetime class for use with JSON serialization."""
from datetime import datetime, timedelta


class DateTime(datetime):
    def json(self):
        return self.isoformat()

    @classmethod
    def from_json(cls, value):
        return datetime.fromisoformat(value)


class TimeDelta(timedelta):
    def json(self):
        return self.total_seconds()

    @classmethod
    def from_json(cls, value):
        return timedelta(seconds=value)
