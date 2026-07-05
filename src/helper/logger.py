import logging
from logging.handlers import TimedRotatingFileHandler


logname = "MonsterPi.log"

log_handler = TimedRotatingFileHandler(
    logname,
    when="midnight",
    backupCount=30,
    encoding="utf-8"
)
log_handler.suffix = "%Y%m%d"

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(module)s.%(funcName)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
