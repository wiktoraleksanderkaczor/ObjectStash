# from datetime import timedelta

# from pydantic import BaseModel, Extra, PositiveInt


# class FailureStrategy(BaseModel):
#     NAME: str

#     class Config:
#         extra: Extra = Extra.allow


# class Await(FailureStrategy):
#     NAME: str = "Await"
#     times: PositiveInt = 3
#     interval: timedelta = timedelta(seconds=5)


# class Fail(FailureStrategy):
#     NAME: str = "Fail"
