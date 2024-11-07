from constants import DB_FILE_NAME, DB_DDL_FILE_NAME, DB_BACKUP_FILE_NAME
from logging import Logger

import os
from pathlib import Path
from sqlite3 import Connection, Cursor
import sqlite3
import sys


class DbMgr:
    def __init__(self, logger: Logger):
        self.logger: Logger = logger

    def get_db_connection(self) -> Connection:
        """ Open and return a DB connection.

        :returns: Connection object to DB
        :raises sqlite3.Error: If it can't connect to the DB
        """
        try:
            self.logger.debug(f"Connecting to DB at {DB_FILE_NAME!r}")
            return sqlite3.connect(DB_FILE_NAME)
        except sqlite3.Error as e:
            self.logger.critical(f"Couldn't connect to database file {DB_FILE_NAME!r}: {e}")
            raise

    def execute_statement(self, statement: str, parms: tuple) -> list[tuple]:
        """ Open a DB connection, execute an SQL statement, close the connection.

        :returns: List of results as tuples
        :raises sqlite3.Error: If something goes wrong with the DB
        """
        log_friendly_statement: str = self.format_statement_for_log(statement)
        self.logger.debug(f"Executing SQL statement: {log_friendly_statement!r} with parms: {parms}")
        conn: Connection = self.get_db_connection()
        try:
            cursor: Cursor = conn.execute(statement, parms)
            conn.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Rolling back. query: {statement!r} | parms: {parms!r} | error: {e}")
            conn.rollback()
            raise
        finally:
            self.logger.debug(f"Closing DB connection")
            conn.close()

    def init_db(self) -> str:
        """ Create an empty DB if it doesn't already exist. If it does, no-op.

        :returns: Message explaining what happened, so instakarma-admin can print it to the console
        :raises sqlite3.Error: If anything goes wrong with the DB
        """
        db_path: Path = Path(DB_FILE_NAME)
        db_ddl_path: Path = Path(DB_DDL_FILE_NAME)

        if db_path.exists():
            msg: str = f"DB already exists at {db_path.name!r}. No changes made."
            self.logger.info(msg)
            return msg
        with self.get_db_connection() as conn:
            with open(db_ddl_path) as ddl_file:
                ddl: str = ddl_file.read()
            try:
                conn.executescript(ddl)
                conn.commit()
            except sqlite3.Error as e:
                msg: str = f"Couldn't create DB: {e}"
                self.logger.critical(msg)
                return msg
            msg: str = f"Created new DB at {db_path.name!r} using DDL {db_ddl_path.name!r}"
            self.logger.info(msg)
            return msg

    def format_statement_for_log(self, statement: str) -> str:
        """ Format a statement as a single line for logging.

        :returns: Statement formatted as a single line
        """
        statement = statement.replace('\n', ' ')  # replace newlines with spaces
        return ' '.join(statement.split())  # replace multiple spaces with a single space

    def backup_db(self) -> None:
        """ Copy the DB file to another local file.

        This should only be called from `instakarma-admin`, so it exits on failure instead of logging and raising.
        """
        db_path: Path = Path(DB_FILE_NAME)
        db_backup_path: Path = Path(DB_BACKUP_FILE_NAME)

        if not db_path.exists():
            sys.exit(f"Error: no DB file at {DB_FILE_NAME!r} to back up. No changes made.")

        if db_backup_path.exists():
            sys.exit(f"Error: DB backup file already exists at {DB_BACKUP_FILE_NAME!r}. No changes made.")

        try:
            with sqlite3.connect(DB_FILE_NAME) as source, sqlite3.connect(DB_BACKUP_FILE_NAME) as destination:
                source.backup(destination)
        except sqlite3.Error as e:
            sys.exit(f"DB not backed up. Error while connecting to DB: {e}")
        print(f"{DB_FILE_NAME!r} backed up to {DB_BACKUP_FILE_NAME!r}")
