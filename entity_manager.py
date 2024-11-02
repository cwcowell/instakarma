
from db_manager import DbManager
from enums import Status
from exceptions import NoSlackApiManagerDefinedError
from slack_api_manager import SlackApiManager

from logging import Logger
from sqlite3 import Cursor
import sqlite3
from typing import Literal

class EntityManager:
    def __init__(self,
                 db_manager: DbManager,
                 logger: Logger,
                 slack_api_manager: SlackApiManager = None):
        self.db_manager: DbManager = db_manager
        self.logger: Logger = logger
        self.slack_api_manager: SlackApiManager = slack_api_manager

    def get_status(self, name: str) -> Status:
        try:
            self.logger.debug(f"Asking DB for status of name '{name}'")
            cursor: Cursor = self.db_manager.execute_statement("""
                                                               SELECT opt_in
                                                               FROM entities
                                                               WHERE name = ?;""",
                                                               (name,))
            result = cursor.fetchone()
            if result:
                status: Status = Status.OPT_IN if result[0] else Status.OPT_OUT
                self.logger.debug(f"DB says status of name '{name}' is '{status}'")
                return status
            else:
                self.logger.info(f"Name '{name}' doesn't exist in 'entities' table")
                raise ValueError
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't get status for name '{name}'")
            raise e

    def change_entity_status(self, name: str, status: Status) -> None:
        try:
            self.db_manager.execute_statement(f"""
                                              UPDATE entities
                                              SET opt_in = {'TRUE' if status == Status.OPT_IN else 'FALSE'}
                                              WHERE name = ?;""",
                                              (name,))
            self.logger.info(f"Entity '{name}' now has status '{status.value}'")
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't set user '{name}' status to '{status.value}': {e}")

    def get_name_from_user_id(self, user_id: str) -> str:
        # if row exists in DB with that `user_id` and `name`, RETURN `name`
        try:
            self.logger.debug(f"Asking DB for name of user_id: '{user_id}'")
            cursor: Cursor = self.db_manager.execute_statement("""
                                                               SELECT name
                                                               FROM entities
                                                               WHERE user_id = ?;""",
                                                               (user_id,))
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't look up 'entity.name' for 'entity.user_id' of '{user_id}': {e}")
            raise e

        first_row_of_results = cursor.fetchone()
        if first_row_of_results:
            name: str = first_row_of_results[0]
            self.logger.debug(f"DB says user_id '{user_id}' has name '{name}'")
            return name

        # else if row exists for that `user_id`, look up `name` in the API and update the row with `name`.
        # RETURN `name`
        try:
            cursor: Cursor = self.db_manager.execute_statement("""
                                                               SELECT * 
                                                               FROM entities
                                                               WHERE user_id = ?;""",
                                                               (user_id,))
        except sqlite3.Error as e:
            self.logger.error("Couldn't look up whether there's a row in 'entities' with "
                              f"'entity.user_id' == '{user_id}': {e}")
            raise e

        first_row_of_results = cursor.fetchone()
        if first_row_of_results:
            self.logger.debug(f"DB has a row for user_id '{user_id}' but the row has no name.")
            if self.slack_api_manager is None:
                raise NoSlackApiManagerDefinedError

            name: str = self.slack_api_manager.get_name_from_slack_api(user_id)
            try:
                self.db_manager.execute_statement("""
                                                  UPDATE entities
                                                  SET name = ?
                                                  WHERE user_id = ?;""",
                                                  (name, user_id))
            except sqlite3.Error as e:
                self.logger.error(f"Couldn't update 'entities' table to set 'name' for 'user_id' of '{user_id}': {e}")
                raise e
            return name

        # else look up the `name` in the API and insert a row with `name` and `user_id`. RETURN `name`
        name: str = self.slack_api_manager.get_name_from_slack_api(user_id)
        self.logger.debug(f"DB has no row for user_id '{user_id}, so adding a new row "
                          f"with that user_id and a name pulled from Slack API")
        try:
            self.db_manager.execute_statement("""
                                              INSERT INTO entities (name, user_id) 
                                              VALUES (?, ?);""",
                                              (name, user_id))
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't insert row into 'entities' table with name '{name}' "
                              f"and user_id '{user_id}': {e}")
            raise e
        return name

    # def get_name_from_slack(self, user_id: str) -> str:
    #     """ Use Slack API to convert a user ID ('U07R69E3YKB') into a user name ('@elvis'). """
    #     self.logger.debug(f"Asking Slack API for name of user with user_id '{user_id}'")
    #     user_info = self.app.client.users_info(user=user_id)
    #     name = user_info['user']['name']
    #     self.logger.debug(f"Slack API returned name '{name}' for user_id '{user_id}'")
    #     name = '@' + name
    #     return name

    def add_entity(self, name: str, user_id: str | None) -> None:
        """Add an entity to the table. No-op if it already exists.

        :raises sqlite3.Error: If something goes wrong with the DB
        """
        try:
            self.db_manager.execute_statement("""
                                              INSERT OR IGNORE INTO entities (name, user_id)
                                              VALUES (?, ?);""",
                                              (name, user_id))
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't add object entity '{name}': {e}")
            raise e

    def list_entities(self, attribute: Literal['karma', 'name']) -> list[tuple[str, int]]:
        """List all entities in the DB.

        :returns: List of tuples, where each tuple contains an entity name and user_id

        :raises sqlite3.Error: If something goes wrong with the DB
        """
        try:
            cursor: Cursor = self.db_manager.execute_statement(f"""
                                         SELECT name, karma
                                         FROM entities
                                         WHERE opt_in = TRUE
                                         ORDER BY {attribute} {'DESC' if attribute == 'karma' else 'ASC'};""",
                                                               ())
        except sqlite3.Error as e:
            self.logger.error(f"Error when retrieving list of entities: {e}")
            raise e
        results = cursor.fetchall()
        entities: list[tuple[str, int]] = []
        for name, karma in results:
            entities.append((name, karma))
        return entities