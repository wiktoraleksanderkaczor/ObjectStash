"""
Logging configuration for the project.
"""
import logging

log = logging.Logger("ObjectStash")
if __debug__:
    LEVEL = logging.DEBUG
else:
    LEVEL = logging.WARNING
log.setLevel(LEVEL)
