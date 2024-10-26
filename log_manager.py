from constants import *

from logging import Logger
import logging.handlers
from logging.handlers import RotatingFileHandler
import os


class LogManager:
    """ Singleton class, so `LogManager.get_logger()` always returns the same `logger` instance. """

    _logger: Logger | None = None

    @staticmethod
    def get_logger() -> Logger:
        if LogManager._logger is None:
            LogManager._logger = LogManager._init_logger()
        return LogManager._logger

    @staticmethod
    def _init_logger():
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)  # make logs dirs, if needed
        logger: Logger = logging.getLogger('instakarma')
        logger.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                                      datefmt='%m/%d/%Y %I:%M:%S %p')
        handler = RotatingFileHandler(filename=LOG_FILE,
                                      mode='a',
                                      maxBytes=LOG_FILE_SIZE,
                                      backupCount=LOG_FILE_COUNT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
