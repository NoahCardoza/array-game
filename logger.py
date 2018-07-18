import logging
import os

logger = logging.getLogger('server')

LOG_DIR = os.getcwd() + '/' + 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_DIR, "server"))
logger.addHandler(fileHandler)

logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)
