from db_manager import DbManager
import response_blocks

from logging import Logger
import sqlite3
from sqlite3 import Connection, Cursor


class ActionManager:

    def __init__(self, db_manager: DbManager, logger: Logger):
        self.db_manager = db_manager
        self.logger = logger

    def show_leaderboard(self, respond, conn: Connection):
        leader_text: str = ''

        try:
            cursor = self.db_manager.execute_query(conn,
                                          """
        SELECT name, karma 
        FROM entities 
        WHERE user_id IS NULL 
        ORDER BY karma DESC;""",
                                          ())
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't get karma of all non-person entities: {e}")
            raise e

        results = cursor.fetchall()
        for result in results:
            name: str = result[0]
            karma: int = result[1]
            leader_text += f"{karma} {name}\n"

        respond(text="show karma of non-person entities",
                blocks=response_blocks.leaderboard(leader_text),
                response_type="ephemeral")
