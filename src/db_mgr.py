from constants import DB_FILE_NAME, DB_DDL_FILE_NAME, DB_BACKUP_FILE_NAME
from logging import Logger
from string_mgr import StringMgr

from pathlib import Path
from sqlite3 import Connection, Cursor
import sqlite3
import sys
from typing import Self, ClassVar


class DbMgr:
    """Collect all DB-related methods in one singleton class."""

    @classmethod
    def execute_statement(cls, statement: str, params: tuple = ()) -> list[tuple]:
        """Execute SQL statement and return results.

        :returns: List of results as tuples
        :raises sqlite3.Error: If something goes wrong with the DB
        """
        instance = cls()

        try:
            cursor: Cursor = instance._connection.execute(statement, params)
            instance._connection.commit()  # no-op for SELECT statements
            return cursor.fetchall()

        except sqlite3.Error as e:
            instance._connection.rollback()
            log_friendly_statement: str = instance.format_statement_for_log(statement)
            instance.logger.error(StringMgr.get_string('db.error.rollback',
                                                   statement=log_friendly_statement,
                                                   parms=params,
                                                   e=e))
            raise

    def __del__(self):
        """Close up the database connection"""
        self._connection.close()

    @classmethod
    def init_db(cls) -> str:
        """Create an empty DB if it doesn't already exist.

        No-op if there is already a DB.

        :returns: Message explaining what happened, so `instakarma-admin` can print it to the console
        :raises sqlite3.Error: If anything goes wrong with the DB
        """

        db_path: Path = Path(DB_FILE_NAME)
        db_ddl_path: Path = Path(DB_DDL_FILE_NAME)

        if db_path.exists():
            msg: str = StringMgr.get_string('db.exists', db_path=db_path.resolve())
            cls.logger.info(msg)
            return msg
        with open(db_ddl_path) as ddl_file:
            ddl: str = ddl_file.read()
        try:
            cls.conn.executescript(ddl)
            cls.conn.commit()
        except sqlite3.Error as e:
            msg: str = StringMgr.get_string('db.error.could-not-create', e=e)
            cls.logger.critical(msg)
            return msg
        msg: str = StringMgr.get_string('db.created-new',
                                        db_path=db_path.resolve(),
                                        db_ddl_path=db_ddl_path.resolve())
        cls.logger.info(msg)
        return msg

    @staticmethod
    def format_statement_for_log(statement: str) -> str:
        """Format a statement as a single line for logging.

        :returns: Statement formatted as a single line
        :raises ValueError: if `statement` isn't a string
        """

        if not isinstance(statement, str):
            raise ValueError(f'Statement must be a string, but got {type(statement)}')
        statement = statement.replace('\n', ' ')  # replace newlines with spaces
        return ' '.join(statement.split())  # replace multiple spaces with a single space

    @classmethod
    def backup_db(cls) -> None:
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
        try:
            cursor: Cursor = self.conn.execute('PRAGMA wal_checkpoint(TRUNCATE);')
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
