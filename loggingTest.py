from Notification.telegram import TelegramAdaptor
import logging

logger = logging.getLogger('me2')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
bot_token = "bot1859381315:AAHr0CuL_qtDO7he7fSeNnHxHwQL_0rTSLQa"
chat_id = "1373157016"
ch = TelegramAdaptor(bot_token,chat_id)
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')