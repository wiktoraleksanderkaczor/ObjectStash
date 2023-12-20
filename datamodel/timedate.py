"""
Custom datetime class for use with data object serialization.
"""
from datetime import datetime, timedelta


class DateTime(datetime):
    def to_data(self):
        return self.isoformat()

    @classmethod
    def from_data(cls, value):
        return datetime.fromisoformat(value)


class TimeDelta(timedelta):
    def to_data(self):
        return self.total_seconds()

    @classmethod
    def from_data(cls, value):
        return timedelta(seconds=value)
