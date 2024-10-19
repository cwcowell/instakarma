import logging.handlers
from logging.handlers import RotatingFileHandler
from logging import Logger
import os
import sqlite3
from sqlite3 import Connection, Cursor
import sys
from typing import Final

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ---
# Constants
# ---

DB_FILE: Final[str] = 'db/instakarma.db'
DB_DDL_FILE: Final[str] = 'db/instakarma_ddl.sql'

LOG_FILE: Final[str] = 'log/instakarma.log'
LOG_FILE_SIZE: Final[int] = 1024 * 1024 * 5
LOG_FILE_COUNT: Final[int] = 3


# ---
# Custom exceptions/errors
# ---

class SelfGrantError(Exception):
    pass


class DisabledEntityError(Exception):
    pass


# ---
# Utilities
# ---

def configure_logger() -> Logger:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)  # make logs dirs, if needed
    logger: Logger = logging.getLogger(__name__)
    logger.setLevel('INFO')
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
    handler = RotatingFileHandler(filename=LOG_FILE,
                                  mode='a',
                                  maxBytes=LOG_FILE_SIZE,
                                  backupCount=LOG_FILE_COUNT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def log_error_and_quit(msg: str) -> None:
    logger.error(msg)
    sys.exit(msg)


# ---
# DB operations
# ---

def get_db_connection() -> Connection:
    try:
        with sqlite3.connect(DB_FILE) as conn:
            return conn
    except sqlite3.Error as e:
        log_error_and_quit(f"Couldn't connect to database file '{DB_FILE}': {e}")


def init_db() -> None:
    if os.path.exists(DB_FILE):
        logger.info(f"Database file '{DB_FILE}' already exists. No changes made.")
        return

    with get_db_connection() as conn:
        with open(DB_DDL_FILE) as ddl_file:
            ddl: str = ddl_file.read()
        try:
            conn.executescript(ddl)
            conn.commit()
            logger.info(f"Creating new DB at '{DB_FILE}' using DDL '{DB_DDL_FILE}'")
        except sqlite3.Error as e:
            log_error_and_quit(f"Error when creating DB: {e}")


def execute_query(conn: Connection, query: str, parms: tuple) -> Cursor:
    try:
        cursor: Cursor = conn.execute(query, parms)
        return cursor
    except sqlite3.Error as e:
        logger.error(f"Rolling back because of error: {e} --- Query: {query} --- Parms: {parms}")
        conn.rollback()
        raise e


# ---
# Helpers
# ---

def add_entity(conn: Connection, entity_name: str) -> None:
    try:
        # Add an entity to the table if it doesn't already exist. Do nothing if it already exists.
        execute_query(conn,
                      """
                      INSERT OR IGNORE INTO entities (entity_name)
                      VALUES (?)
                      """,
                      (entity_name,))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Couldn't add entity '{entity_name}': {e}")
        raise e


def is_entity_disabled(conn: Connection, entity: str) -> bool:
    try:
        cursor: Cursor = execute_query(conn,
                                       """
                                       SELECT disabled
                                       FROM entities 
                                       WHERE entity_name = ?
                                       """,
                                       (entity,))
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        logger.error(f"Error when checking if '{entity}' is disabled: {e}")
        raise e


def extract_recipients(msg_text: str, action: str) -> list[str]:
    recipients: list[str] = []
    words: list[str] = msg_text.split()
    for word in words:
        if word.endswith(action):
            recipient: str = word[:-len(action)]
            if recipient:
                recipients.append(recipient)
    return recipients


def detect_granter_and_recipients(msg_details: dict, action: str) -> (str, list[str]):
    granter: str = msg_details['user']
    msg_text: str = msg_details['text']
    recipients: list[str] = extract_recipients(msg_text, action)
    return granter, recipients


# ---
# Karma logic
# ---

def get_karma(conn: Connection, entity: str) -> int:
    try:
        cursor: Cursor = execute_query(conn,
                                       """
                                       SELECT karma
                                       FROM entities
                                       WHERE entity_name = ? AND disabled = FALSE
                                       """,
                                       (entity,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            logger.info(f"Entity '{entity}' is disabled or doesn't exist in 'entities' table")
            raise ValueError

    except sqlite3.Error as e:
        logger.error(f"Couldn't get karma for '{entity}'")
        raise e


def grant_karma(conn: Connection, granter: str, recipient: str, amount: int) -> None:
    if granter == recipient:
        logger.info(f"Entity '{granter}' can't grant self-karma")
        raise SelfGrantError

    add_entity(conn, granter)
    add_entity(conn, recipient)

    if is_entity_disabled(conn, recipient):
        logger.info(f"Can't grant karma to disabled entity '{recipient}'")
        raise DisabledEntityError

    try:
        # make an entry in the 'grants' table using subqueries to look up 'entity_id' for granter and recipient
        execute_query(conn,
                      """
                      INSERT INTO grants (granter_id, recipient_id, amount)
                      SELECT
                          (SELECT entity_id FROM entities WHERE entity_name = ?),
                          (SELECT entity_id FROM entities WHERE entity_name = ?),
                          ?
                      """,
                      (granter, recipient, amount))
        # make an entry in the 'entities' table, which tracks total karma for each user
        execute_query(conn,
                      """
                      UPDATE entities
                      SET karma = karma + ?
                      WHERE entity_name = ?
                      """,
                      (amount, recipient))
        conn.commit()
        logger.info(f'{granter} granted {amount} karma to {recipient}')

    except sqlite3.Error as e:
        logger.error(f"Error when granting '{amount}' karma from '{granter}' to '{recipient}': {e}")
        raise e


# ---
# Main logic
# ---

app: App = App(token=os.environ.get("SLACK_BOT_TOKEN"))


# Listen for "++" in any message in any channel the bot subscribes to.
@app.message(r'\+\+')
def add_karma_handler(message: dict, say) -> None:
    granter: str
    recipients: list[str]
    granter, recipients = detect_granter_and_recipients(message, '++')
    with get_db_connection() as conn:
        for recipient in recipients:
            grant_karma(conn, granter, recipient, 1)
            recipient_total_karma: int = get_karma(conn, recipient)
            say(f"{recipient} leveled up ({recipient_total_karma} karma)")


# # Listen for "--" in any message in any channel the bot subscribes to.
# @app.message(r'\-\-')
# def subtract_karma_handler(msg_details: dict, say) -> None:
#     msg_text: str = msg_details['text']
#     total_karma: int = 0
#     recipient: str = extract_recipient(msg_text, '++')
#     if recipient:
#         say(f"{recipient} leveled up ({total_karma} karma)")


if __name__ == "__main__":
    logger = configure_logger()
    init_db()  # non-destructively create a DB if it isn't there already
    SocketModeHandler(app=app,
                      app_token=os.environ["SLACK_APP_TOKEN"]).start()
