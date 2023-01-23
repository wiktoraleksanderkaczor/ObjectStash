"""Interface for replacement policy."""

from abc import ABC  # , abstractmethod


# Define model for getting which items in cache will need replaced.
class ReplacementInterface(ABC):
    pass
