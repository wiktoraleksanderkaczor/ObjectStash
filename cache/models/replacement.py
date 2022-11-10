# Define model for getting which items in cache will need replaced.
from pydantic import Protocol


class Replacement(Protocol):
    pass
