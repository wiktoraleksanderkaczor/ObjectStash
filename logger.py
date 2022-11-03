import logging

log = logging.Logger("ObjectStash")
if __debug__:
    level = logging.DEBUG
else:
    level = logging.WARNING
log.setLevel(level)
