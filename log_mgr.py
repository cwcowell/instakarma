from constants import LOG_FILE, LOG_LEVEL, LOG_FILE_SIZE, LOG_FILE_COUNT
from logging import Logger
import logging.handlers
from logging.handlers import RotatingFileHandler
import pathlib


class LogMgr:
    """Singleton class, so `LogMgr.get_logger()` always returns the same `logger` instance."""

    _logger: Logger | None = None

    def __new__(cls):
        """Prevent instantiation of this class."""

        raise Exception("LogMgr class cannot be instantiated. Use `LogMgr.get_logger()` instead.")

    @classmethod  # needs access to `_logger` so it must be class instead of static
    def get_logger(cls,
                   name: str,
                   log_file: str = LOG_FILE,
                   log_level: str = LOG_LEVEL,
                   log_file_size: int = LOG_FILE_SIZE,
                   log_file_count: int = LOG_FILE_COUNT) -> Logger:
        """Retrieve the single logger instance used throughout instakarma-bot.

        :returns Logger: The instakarma-bot logger
        """

        if LogMgr._logger is None:
            LogMgr._logger = LogMgr._init_logger(name, log_file, log_level, log_file_size, log_file_count)
        return LogMgr._logger

    @staticmethod  # doesn't need access to class state, so can be static
    def _init_logger(name: str,
                     log_file: str = LOG_FILE,
                     log_level: str = LOG_LEVEL,
                     log_file_size: int = LOG_FILE_SIZE,
                     log_file_count: int = LOG_FILE_COUNT):
        """Make the single logger if it doesn't exist as a class variable yet."""

        log_path = pathlib.Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)  # make parent dir(s) if needed
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
