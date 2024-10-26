from constants import DB_FILE, DB_DDL_FILE
from logging import Logger

import logging
import os
from sqlite3 import Connection, Cursor
import sqlite3
import sys

from slack_bolt.adapter.socket_mode import SocketModeHandler


class DbManager:
    def __init__(self, logger: Logger, handler: SocketModeHandler):
        self.logger: Logger = logger
        self.handler: SocketModeHandler = handler

    def get_db_connection(self) -> Connection:
        try:
            self.logger.debug(f"Connecting to DB at '{DB_FILE}'")
            with sqlite3.connect(DB_FILE) as conn:
                return conn
        except sqlite3.Error as e:
            self.logger.critical(f"Couldn't connect to database file '{DB_FILE}': {e}")

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

    def execute_query(self, conn: Connection, query: str, parms: tuple) -> Cursor:
        try:
            self.logger.debug(f"Executing SQL query: '{query}' with parms: '{parms}'")
            cursor: Cursor = conn.execute(query, parms)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            self.logger.error(f"Rolling back. query: {query} | parms: '{parms}' | error: {e}")
            conn.rollback()
            raise e
