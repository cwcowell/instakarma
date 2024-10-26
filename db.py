from constants import DB_FILE, DB_DDL_FILE

import os
from sqlite3 import Connection, Cursor
import sqlite3

# ---
# DB utilities
# ---

def get_db_connection() -> Connection:
    try:
        logger.debug(f"Connecting to DB at '{DB_FILE}'")
        with sqlite3.connect(DB_FILE) as conn:
            return conn
    except sqlite3.Error as e:
        log_critical_error_and_quit(f"Couldn't connect to database file '{DB_FILE}': {e}")


def init_db() -> None:
    if os.path.exists(DB_FILE):
        logger.info(f"Database already exists at '{DB_FILE}'. No changes made.")
        return

    with get_db_connection() as conn:
        with open(DB_DDL_FILE) as ddl_file:
            ddl: str = ddl_file.read()
        try:
            logger.info(f"Creating new DB at '{DB_FILE}' using DDL '{DB_DDL_FILE}'")
            conn.executescript(ddl)
            conn.commit()
        except sqlite3.Error as e:
            log_critical_error_and_quit(f"Couldn't create DB: {e}")


def execute_query(conn: Connection, query: str, parms: tuple) -> Cursor:
    try:
        logger.debug(f"Executing SQL query: '{query}' with parms: '{parms}'")
        cursor: Cursor = conn.execute(query, parms)
        conn.commit()
        return cursor
    except sqlite3.Error as e:
        logger.error(f"Rolling back. query: {query} | parms: '{parms}' | error: {e}")
        conn.rollback()
        raise e


