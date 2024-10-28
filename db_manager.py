from constants import DB_FILE, DB_DDL_FILE
from logging import Logger

import os
from sqlite3 import Connection, Cursor
import sqlite3

from slack_bolt.adapter.socket_mode import SocketModeHandler


class DbManager:
    def __init__(self, logger: Logger, handler: SocketModeHandler):
        self.logger: Logger = logger
        self.handler: SocketModeHandler = handler

    def execute_statement(self, statement: str, parms: tuple) -> Cursor:
        log_friendly_statement: str = self.format_statement_for_log(statement)
        self.logger.debug(f"Executing SQL statement: '{log_friendly_statement}' with parms: '{parms}'")
        conn: Connection = self.get_db_connection()
        try:
            cursor: Cursor = conn.execute(statement, parms)
            conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Rolling back. query: {statement} | parms: '{parms}' | error: {e}")
            conn.rollback()
            raise e
        return cursor

    def get_db_connection(self) -> Connection:
        try:
            self.logger.debug(f"Connecting to DB at '{DB_FILE}'")
            return sqlite3.connect(DB_FILE)
        except sqlite3.Error as e:
            self.logger.critical(f"Couldn't connect to database file '{DB_FILE}': {e}")

    def format_statement_for_log(self, sql: str) -> str:
        """ SQL statements in this code are indented and have newlines.
        Format them as a single line just for logging.
        """
        sql = sql.replace('\n', ' ')  # replace newlines returns with spaces
        return ' '.join(sql.split())  # replace multiple spaces with a single space

    def init_db(self) -> None:
        if os.path.exists(DB_FILE):
            self.logger.info(f"Database already exists at '{DB_FILE}'. No changes made.")
            return
        with self.get_db_connection() as conn:
            with open(DB_DDL_FILE) as ddl_file:
                ddl: str = ddl_file.read()
            try:
                self.logger.info(f"Creating new DB at '{DB_FILE}' using DDL '{DB_DDL_FILE}'")
                conn.executescript(ddl)
                conn.commit()
            except sqlite3.Error as e:
                self.logger.critical(f"Couldn't create DB: {e}")
