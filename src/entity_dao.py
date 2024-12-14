from db_mgr import DbMgr
from enums import Status
from slack_api_mgr import SlackApiMgr
from string_mgr import StringMgr

from logging import Logger
import sqlite3
from typing import Literal

from slack_sdk.errors import SlackApiError


class EntityDao:
    def __init__(self,
                 db_mgr: DbMgr,
                 logger: Logger,
                 slack_api_mgr: SlackApiMgr = None):
        self.db_mgr: DbMgr = db_mgr
        self.logger: Logger = logger
        self.slack_api_mgr: SlackApiMgr = slack_api_mgr

    def get_status(self, name: str) -> Status:
        """Get the status of an entity, identifying it by name.

        :returns: Status of the entity
        :raises sqlite3.error: If something goes wrong with the DB
        """

        try:
            results: list = self.db_mgr.execute_statement("""
                                                          SELECT opted_in
                                                          FROM entities
                                                          WHERE name = ?;""",
                                                          (name,))
            result: list = results[0]
            if result:
                status: Status = Status.OPTED_IN if result[0] else Status.OPTED_OUT
                return status
            else:
                self.logger.info(StringMgr.get_string('entity.error.not-in-db', name=name))
                raise ValueError
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('entity.error.no-status', name=name, e=e))
            raise

    def name_exists_in_db(self, name: str) -> bool:
        """See if an entity with a particular name exists in the 'entities' table.

        :returns: Whether the name exists in the DB
        :raises sqlite3.error: If something goes wrong with the DB
        """

        try:
            results: list = self.db_mgr.execute_statement("""
                                                          SELECT *
                                                          FROM entities
                                                          WHERE name = ?;""",
                                                          (name,))
            exists: bool = len(results) > 0
            return exists
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('entity.error.could-not-check-name', name=name, e=e))
            raise

    def set_status(self, name: str, new_status: Status) -> None:
        """Set an entity's opted-in/opted-out status.

        :raises sqlite3.error: If something goes wrong with the DB
        """

        try:
            self.db_mgr.execute_statement(f"""
                                           UPDATE entities
                                           SET opted_in = {'TRUE' if new_status == Status.OPTED_IN else 'FALSE'}
                                           WHERE name = ?;""",
                                           (name,))
            self.logger.info(StringMgr.get_string('entity.current-status', name=name, status=new_status.value))
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('entity.error.could-not-set-status',
                                                   name=name,
                                                   status=new_status.value,
                                                   e=e))
            raise

    def get_name_from_user_id(self, user_id: str) -> str:
        """ Convert an entity's user_id to its name.

        Consult the DB and/or Slack API and add DB entries as needed.

        :returns: Name corresponding to the provided user_id
        :raises sqlite3.error: If something goes wrong with the DB
        """

        # if row exists in DB with that user_id and name, return name
        try:
            results: list = self.db_mgr.execute_statement("""
                                                          SELECT name
                                                          FROM entities
                                                          WHERE user_id = ?;""",
                                                          (user_id,))
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('entity.error.could-not-get-name-from-user-id',
                                                   user_id=user_id,
                                                   e=e))
            raise

        if len(results):
            name: str = results[0][0]
            if name:
                return name
            else:
                # else if row exists for that `user_id` but it has no value for 'name',
                # look up `name` in the API, update the row with `name`, and return the `name`
                try:
                    name: str = self.slack_api_mgr.get_name_from_slack_api(user_id)
                except SlackApiError:
                    raise
                try:
                    self.db_mgr.execute_statement("""
                                                  UPDATE entities
                                                  SET name = ?
                                                  WHERE user_id = ?;""",
                                                  (name, user_id))
                except sqlite3.Error as e:
                    self.logger.error(StringMgr.get_string('entity.error.could-not-set-name',
                                                           name=name,
                                                           user_id=user_id,
                                                           e=e))
                    raise
                return name
        # else insert a row with name and user_id and return name
        try:
            name: str = self.slack_api_mgr.get_name_from_slack_api(user_id)
        except SlackApiError:
            raise
        try:
            self.db_mgr.execute_statement("""
                                          INSERT INTO entities (name, user_id)
                                          VALUES (?, ?);""",
                                          (name, user_id))
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('entity.error.could-not-add-name-and-user-id',
                                                   name=name,
                                                   user_id=user_id,
                                                   e=e))
            raise
        return name

    def add_entity(self, name: str, user_id: str | None) -> None:
        """Add an entity to the table.

        No-op if it already exists. Store the user_id in the entity's row if it was passed in.

        :raises sqlite3.Error: If something goes wrong with the DB
        """

        try:
            self.db_mgr.execute_statement("""
                                          INSERT OR IGNORE INTO entities (name, user_id)
                                          VALUES (?, ?);""",
                                          (name, user_id))
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('entity.error.could-not-add-entity',
                                                   name=name,
                                                   user_id=user_id,
                                                   e=e))
            raise

    def list_entities(self, attribute: Literal['karma', 'name']) -> list[tuple[str, int]]:
        """List all entities in the DB either alphabetically or by descending karma.

        :returns: List of tuples, where each tuple contains an entity name and user_id
        :raises sqlite3.Error: If something goes wrong with the DB
        """

        try:
            results: list = self.db_mgr.execute_statement(f"""
                                         SELECT name, karma
                                         FROM entities
                                         WHERE opted_in = TRUE
                                         ORDER BY {attribute} {'DESC' if attribute == 'karma' else 'ASC'};""",
                                                          ())
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('entity.error.could-not-list-entities', e=e))
            raise
        entities: list[tuple[str, int]] = [(name, karma) for name, karma in results]
        return entities

    def list_opted_out_entities(self) -> list[str]:
        """List all entities in the DB with 'opted-out' status.

        :returns: List of tuples, each containing an opted-out entity name and user_id
        :raises sqlite3.error: If something goes wrong with the DB
        """

        try:
            results: list = self.db_mgr.execute_statement(f"""
                                                          SELECT name
                                                          FROM entities
                                                          WHERE opted_in = FALSE
                                                          ORDER BY name;""",
                                                          ())
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('entity.error.could-not-list-opted-out', e=e))
            raise
        entities: list[str] = [result[0] for result in results]
        return entities
