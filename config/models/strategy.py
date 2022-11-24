from datetime import timedelta

from pydantic import BaseModel, Extra, PositiveInt, root_validator


class FailureStrategy(BaseModel):
    action: str

    @root_validator(pre=True)
    def set_action_name(cls, values):
        values["action"] = cls.__name__
        return values

    class Config:
        extra: Extra = Extra.allow


class Await(FailureStrategy):
    times: PositiveInt = 3
    interval: timedelta = timedelta(seconds=5)


class Fail(FailureStrategy):
    pass
