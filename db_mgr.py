from constants import DB_FILE, DB_DDL_FILE, DB_FILE_BACKUP
from logging import Logger

import os
from sqlite3 import Connection, Cursor
import sqlite3


class DbMgr:
    def __init__(self, logger: Logger):
        self.logger: Logger = logger

    def execute_statement(self, statement: str, parms: tuple) -> list:
        """ Open a DB connection, execute an SQL statement, close the connection.

        :returns: list of results
        :raises sqlite3.Error: If something goes wrong with the DB
        """
        log_friendly_statement: str = self.format_statement_for_log(statement)
        self.logger.debug(f"Executing SQL statement: '{log_friendly_statement}' with parms: '{parms}'")
        conn: Connection = self.get_db_connection()
        try:
            cursor: Cursor = conn.execute(statement, parms)
            conn.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Rolling back. query: {statement} | parms: '{parms}' | error: {e}")
            conn.rollback()
            raise e
        finally:
            conn.close()

    # TODO: should I see if I can make more methods static? Is there any advantage to that?
    def get_db_connection(self) -> Connection:
        """ Open and return a DB connection.

        :returns: Connection object to DB
        :raises sqlite3.Error: If it can't connect to the DB
        """
        try:
            self.logger.debug(f"Connecting to DB at '{DB_FILE}'")
            return sqlite3.connect(DB_FILE)
        except sqlite3.Error as e:
            self.logger.critical(f"Couldn't connect to database file '{DB_FILE}': {e}")
            raise e

    def format_statement_for_log(self, statement: str) -> str:
        """ SQL statements in this code are indented and have newlines.
        Format them as a single line just for logging.
        """
        statement = statement.replace('\n', ' ')  # replace newlines with spaces
        return ' '.join(statement.split())  # replace multiple spaces with a single space

    def init_db(self) -> str:
        if os.path.exists(DB_FILE):
            msg: str = f"Database already exists at '{DB_FILE}'. No changes made."
            self.logger.info(msg)
            return msg
        with self.get_db_connection() as conn:
            with open(DB_DDL_FILE) as ddl_file:
                ddl: str = ddl_file.read()
            try:
                conn.executescript(ddl)
                conn.commit()
                msg: str = f"Created new DB at '{DB_FILE}' using DDL '{DB_DDL_FILE}'"
                self.logger.info(msg)
                return msg
            except sqlite3.Error as e:
                msg: str = f"Couldn't create DB: {e}"
                self.logger.critical(msg)
                return msg

    def backup_db(self) -> None:
        with sqlite3.connect(DB_FILE) as source, sqlite3.connect(DB_FILE_BACKUP) as destination:
            source.backup(destination)
        msg: str = f"'{DB_FILE}' backed up to '{DB_FILE_BACKUP}'"
        print(msg)
        self.logger.info(msg)