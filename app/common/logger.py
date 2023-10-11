import logging, coloredlogs
# from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

coloredlogs.install(level='INFO', fmt='%(asctime)s %(levelname)s %(message)s', milliseconds=True)

# OR use the basic one!
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(levelname)s %(message)s',
#                     # filename='app.log',
#                     # filemode='w'
#                     )
# OR use the handler
# handler = SysLogHandler(address=('localhost', 514)) # address='/dev/log',
# handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
# handler.setLevel(logging.INFO)

# logger.info('This is an info message')
# logger.debug('This is a debug message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')

