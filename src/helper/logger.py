
import logging
from logging.handlers import TimedRotatingFileHandler


logname = 'MonsterPi.log'
log_handler = TimedRotatingFileHandler(logname, when='midnight', backupCount=30)
log_handler.suffix = "%Y%m%d"
logger = logging.getLogger('DailyLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
