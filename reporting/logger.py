"""
Logging configuration for the project.
"""
import logging

logger = logging.Logger("Pioneer")
if __debug__:
    LEVEL = logging.DEBUG
else:
    LEVEL = logging.WARNING
logger.setLevel(LEVEL)
