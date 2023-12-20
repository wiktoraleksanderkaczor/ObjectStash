"""
Logging configuration for the project.
"""
import logging

from settings import config

logger = logging.Logger("vint")
if __debug__ or config.runtime.debug:
    LEVEL = logging.DEBUG
else:
    LEVEL = logging.WARNING
logger.setLevel(LEVEL)
