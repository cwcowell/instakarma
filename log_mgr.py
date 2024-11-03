from constants import *

from logging import Logger
import logging.handlers
from logging.handlers import RotatingFileHandler
import os


class LogManager:
    """ Singleton class, so `LogManager.get_logger()` always returns the same `logger` instance. """

    _logger: Logger | None = None

    @staticmethod
    def get_logger(name: str,
                   log_file: str,
                   log_level: str,
                   log_file_size: int,
                   log_file_count: int) -> Logger:
        if LogManager._logger is None:
            LogManager._logger = LogManager._init_logger(name, log_file, log_level, log_file_size, log_file_count)
        return LogManager._logger

    @staticmethod
    def _init_logger(name: str,
                     log_file: str,
                     log_level: str,
                     log_file_size: int,
                     log_file_count: int):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)  # make logs dirs, if needed
        logger: Logger = logging.getLogger(name)
        logger.setLevel(log_level)
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                                      datefmt='%m/%d/%Y %I:%M:%S %p')
        handler = RotatingFileHandler(filename=log_file,
                                      mode='a',
                                      maxBytes=log_file_size,
                                      backupCount=log_file_count)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
