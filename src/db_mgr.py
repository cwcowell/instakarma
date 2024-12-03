from constants import DB_FILE_NAME, DB_DDL_FILE_NAME, DB_BACKUP_FILE_NAME
from logging import Logger
from string_mgr import StringMgr

from pathlib import Path
from sqlite3 import Connection, Cursor
import sqlite3
import sys

# ---
# class Singleton:
#     _field = 7
#
#     def __new__(cls, *args, **kwargs):
#         raise NotImplementedError("This class cannot be instantiated")
#
#     @classmethod
#     def get_field(cls):
#         return cls._field
#
# ---

class DbMgr:
    """Collect all DB-related methods in one class."""

    def __init__(self, logger: Logger):
        self.logger: Logger = logger

    def get_db_connection(self) -> Connection:
        """Open and return a DB connection.

        :returns: Connection object to DB
        :raises sqlite3.Error: If it can't connect to the DB
        """
        try:
            return sqlite3.connect(DB_FILE_NAME)
        except sqlite3.Error as e:
            self.logger.critical(StringMgr.get_string('db.error.connection', db_file_name=DB_FILE_NAME, e=e))
            raise

    def execute_statement(self, statement: str, parms: tuple) -> list[tuple]:
        """Open a DB connection, execute an SQL statement, close the connection.

        :returns: List of results as tuples
        :raises sqlite3.Error: If something goes wrong with the DB
        """

        log_friendly_statement: str = self.format_statement_for_log(statement)
        with self.get_db_connection() as conn:
            try:
                cursor: Cursor = conn.execute(statement, parms)
                conn.commit()
                return cursor.fetchall()
            except sqlite3.Error as e:
                conn.rollback()
                self.logger.error(StringMgr.get_string('db.error.rollback',
                                                       statement=log_friendly_statement,
                                                       parms=parms, e=e))
                raise

    def init_db(self) -> str:
        """Create an empty DB if it doesn't already exist.

        No-op if there is already a DB.

        :returns: Message explaining what happened, so `instakarma-admin` can print it to the console
        :raises sqlite3.Error: If anything goes wrong with the DB
        """

        db_path: Path = Path(DB_FILE_NAME)
        db_ddl_path: Path = Path(DB_DDL_FILE_NAME)

        if db_path.exists():
            msg: str = StringMgr.get_string('db.exists', db_path=db_path.resolve())
            self.logger.info(msg)
            return msg
        with self.get_db_connection() as conn:
            with open(db_ddl_path) as ddl_file:
                ddl: str = ddl_file.read()
            try:
                conn.executescript(ddl)
                conn.commit()
            except sqlite3.Error as e:
                msg: str = StringMgr.get_string('db.error.could-not-create', e=e)
                self.logger.critical(msg)
                return msg
            msg: str = StringMgr.get_string('db.created-new',
                                            db_path=db_path.resolve(),
                                            db_ddl_path=db_ddl_path.resolve())
            self.logger.info(msg)
            return msg

    def format_statement_for_log(self, statement: str) -> str:
        """Format a statement as a single line for logging.

        :returns: Statement formatted as a single line
        :raises ValueError: if `statement` isn't a string
        """

        if not isinstance(statement, str):
            raise ValueError(f'Statement must be a string, but got {type(statement)}')
        statement = statement.replace('\n', ' ')  # replace newlines with spaces
        return ' '.join(statement.split())  # replace multiple spaces with a single space

    def backup_db(self) -> None:
        """Copy the DB file to another local file.

        This should only be called from `instakarma-admin`, so it exits on failure instead of logging and raising.
        """

        db_path: Path = Path(DB_FILE_NAME)
        db_backup_path: Path = Path(DB_BACKUP_FILE_NAME)

        if not db_path.exists():
            sys.exit(StringMgr.get_string('db.error.no-db-file', db_path=db_path))

        if db_backup_path.exists():
            sys.exit(StringMgr.get_string('db.error.db-backup-file-exists', db_backup_path=db_backup_path))

        # checkpoint to truncate WAL and consolidate DB to 1 file
        with self.get_db_connection() as conn:
            try:
                cursor: Cursor = conn.execute('PRAGMA wal_checkpoint(TRUNCATE);')
                results: tuple[int, int, int] = cursor.fetchone()
                if results[0]:
                    sys.exit(StringMgr.get_string('db.error.truncation-blocked'))
                print(StringMgr.get_string('db.truncated', single_db_file=db_path.resolve()))
            except sqlite3.Error as e:
                sys.exit(StringMgr.get_string('db.error.could-not-truncate', e=e))

        try:
            with sqlite3.connect(DB_FILE_NAME) as source, \
                 sqlite3.connect(DB_BACKUP_FILE_NAME) as destination:
                source.backup(destination)
        except sqlite3.Error as e:
            sys.exit(StringMgr.get_string('db.error.could-not-backup', e=e))

        print(StringMgr.get_string('db.backed-up',
                                   db_file_path=db_path.resolve(),
                                   db_backup_file_path=db_backup_path.resolve()))
