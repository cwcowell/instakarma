from db_mgr import DbMgr
from enums import Status
from exceptions import NoSlackApiMgrDefinedError
from slack_api_mgr import SlackApiMgr

from logging import Logger
import sqlite3
from typing import Literal

from slack_sdk.errors import SlackApiError


class EntityMgr:
    def __init__(self,
                 db_mgr: DbMgr,
                 logger: Logger,
                 slack_api_mgr: SlackApiMgr = None):
        self.db_mgr: DbMgr = db_mgr
        self.logger: Logger = logger
        self.slack_api_mgr: SlackApiMgr = slack_api_mgr

    def get_status(self, name: str) -> Status:
        try:
            self.logger.debug(f"asking DB for status of {name!r}")
            results: list = self.db_mgr.execute_statement("""
                                                               SELECT opted_in
                                                               FROM entities
                                                               WHERE name = ?;""",
                                                          (name,))
            result: list = results[0]
            if result:
                status: Status = Status.OPTED_IN if result[0] else Status.OPTED_OUT
                self.logger.debug(f"DB says status of {name!r} is {status!r}")
                return status
            else:
                self.logger.info(f"{name!r} doesn't exist in 'entities' table")
                raise ValueError
        except sqlite3.Error as e:
            self.logger.error(f"couldn't get status for {name!r}: {e}")
            raise e

    def name_exists_in_db(self, name: str) -> bool:
        """ See if an entity with a particular name exists in the 'entities' table.

        :returns: Whether the name exists in the DB
        """
        try:
            results: list = self.db_mgr.execute_statement("""
                                          SELECT *
                                          FROM entities
                                          WHERE name = ?;""",
                                          (name, ))
            exists: bool = len(results) > 0
            # msg: str = f"{name!r} exists in 'entities' table" if exists else f"{name!r} doesn't exist in 'entities' table"
            msg: str = f"{name!r} {"exists" if exists else "doesn't exist"} in 'entities' table"
            self.logger.debug(msg)
            return exists
        except sqlite3.Error as e:
            self.logger.error(f"couldn't check if {name!r} exists in 'entities' table: {e}")
            raise

    def set_status(self, name: str, new_status: Status) -> None:
        """ Set an entity's opted-in/opted-out status. """
        try:
            self.db_mgr.execute_statement(f"""
                                              UPDATE entities
                                              SET opted_in = {'TRUE' if new_status == Status.OPTED_IN else 'FALSE'}
                                              WHERE name = ?;""",
                                          (name,))
            self.logger.info(f"{name!r} now has status {new_status.value!r}")
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't set user {name!r} status to {new_status.value!r}: {e}")
            raise

    def get_name_from_user_id(self, user_id: str) -> str:
        """ Convert an entity's user_id to its name.

        Consult the DB and/or Slack API and add DB entries as needed.
        :returns: The name that corresponds to the provided user_id
        """

        # if row exists in DB with that user_id and name, RETURN name
        try:
            self.logger.debug(f"asking DB for name of user_id: {user_id!r}")
            results: list = self.db_mgr.execute_statement("""
                                                                   SELECT name
                                                                   FROM entities
                                                                   WHERE user_id = ?;""",
                                                             (user_id,))
        except sqlite3.Error as e:
            self.logger.error(f"couldn't look up 'entity.name' for 'entity.user_id' of {user_id!r}: {e}")
            raise e

        if len(results):
            name: str = results[0][0]
            self.logger.debug(f"DB says user_id {user_id!r} has name {name!r}")
            return name

        # else if row exists for that `user_id`, look up `name` in the API and update the row with `name`.
        # RETURN `name`
        try:
            results: list = self.db_mgr.execute_statement("""
                                                               SELECT *
                                                               FROM entities
                                                               WHERE user_id = ?;""",
                                                          (user_id,))
        except sqlite3.Error as e:
            self.logger.error("couldn't look up whether there's a row in 'entities' with "
                              f"'entity.user_id' of {user_id!r}: {e}")
            raise

        if results:
            self.logger.debug(f"DB has a row for user_id {user_id!r} but the row has no name")
            if self.slack_api_mgr is None:
                raise NoSlackApiMgrDefinedError
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
                self.logger.error(f"couldn't update 'entities' table to set 'name' for 'user_id' of {user_id!r}: {e}")
                raise
            return name

        # else look up name in the API and insert a row with name and user_id, and return name
        try:
            name: str = self.slack_api_mgr.get_name_from_slack_api(user_id)
        except SlackApiError:
            raise
        self.logger.debug(f"DB has no row for 'user_id' of {user_id!r}, so adding a new row "
                          f"with that user_id and a name pulled from Slack API")
        try:
            self.db_mgr.execute_statement("""
                                          INSERT INTO entities (name, user_id)
                                          VALUES (?, ?);""",
                                    (name, user_id))
        except sqlite3.Error as e:
            self.logger.error(f"couldn't insert row into 'entities' table with name {name!r} "
                              f"and user_id {user_id!r}: {e}")
            raise
        return name

    def add_entity(self, name: str, user_id: str | None) -> None:
        """Add an entity to the table. No-op if it already exists.

        :raises sqlite3.Error: If something goes wrong with the DB
        """
        self.logger.debug(f"adding entity {name!r} to DB")
        try:
            self.db_mgr.execute_statement("""
                                          INSERT OR IGNORE INTO entities (name, user_id)
                                          VALUES (?, ?);""",
                                      (name, user_id))
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't add object entity {name!r}: {e}")
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
            self.logger.error(f"couldn't retrieve list of entities: {e}")
            raise
        entities: list[tuple[str, int]] = [(name, karma) for name, karma in results]
        return entities

    def list_opted_out_entities(self) -> list[str]:
        """ List all entities in the DB with 'opted-out' status.

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
            self.logger.error(f"couldn't retrieve list of opted-out entities: {e}")
            raise
        entities: list[str] = [result[0] for result in results]
        return entities
