from database.models.database import Database


class Timeseries(Database):
    def __init__(self, name: str) -> None:
        super().__init__(name)
