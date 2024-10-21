from constants import *

import logging.handlers
from logging import Logger
from logging.handlers import RotatingFileHandler
import os
import sys

def init_logger() -> Logger:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)  # make logs dirs, if needed
    logger: Logger = logging.getLogger(__name__)
    logger.setLevel('INFO')
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
    handler = RotatingFileHandler(filename=LOG_FILE,
                                  mode='a',
                                  maxBytes=LOG_FILE_SIZE,
                                  backupCount=LOG_FILE_COUNT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def log_error_and_quit(msg: str) -> None:
    logger.error(msg)
    sys.exit(msg)
