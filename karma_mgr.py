from constants import NUM_TOP_GRANTERS, NUM_TOP_RECIPIENTS
from db_mgr import DbMgr
from entity_mgr import EntityMgr
from exceptions import OptedOutRecipientError, OptedOutGranterError
from enums import Status

from logging import Logger
import sqlite3


class KarmaMgr:

    def __init__(self,
                 db_mgr: DbMgr,
                 entity_mgr: EntityMgr,
                 logger: Logger):
        self.db_mgr = db_mgr
        self.entity_mgr = entity_mgr
        self.logger = logger

    def get_karma(self, name: str) -> int:
        """ Get the current karma for any entity, whether person or object.

        :return: The entity's current karma
        :raises sqlite3.Error: If anything goes wrong with the DB
        :raises ValueError: If there's no entity with that name in the DB, or if they have opted-out status
        """
        try:
            results: list = self.db_mgr.execute_statement("""
                                                          SELECT karma
                                                          FROM entities
                                                          WHERE name = ? AND opted_in = TRUE;""",
                                                          (name,))
            if results[0]:
                return results[0][0]
            else:
                msg: str = f"{name!r} is opted-out or doesn't exist in 'entities' table"
                self.logger.info(msg)
                raise ValueError(msg)
        except sqlite3.Error as e:
            self.logger.error(f"couldn't get karma for {name!r}: {e}")
            raise

    def get_top_granters(self, recipient_name: str) -> list[tuple[str, int]]:
        try:
            results: list = self.db_mgr.execute_statement(f"""
                                               SELECT e_granter.name as top_granter_name,
                                                      COUNT(*) as times_granted
                                               FROM grants g
                                               JOIN entities e_granter ON g.granter_id = e_granter.entity_id
                                               JOIN entities e_recipient ON g.recipient_id = e_recipient.entity_id
                                               WHERE e_recipient.name = ?
                                               GROUP BY g.granter_id
                                               ORDER BY times_granted DESC, top_granter_name
                                               LIMIT {NUM_TOP_GRANTERS};""",
                                                          (recipient_name,))

            return [(name, int(num_grants)) for name, num_grants in results]
        except sqlite3.Error as e:
            self.logger.error(f"couldn't get biggest granters to {recipient_name!r}: {e}")
            raise

    def get_top_recipients(self, granter_name: str) -> list[tuple[str, int]]:
        try:
            results: list = self.db_mgr.execute_statement(f"""
                                         SELECT e_recipient.name as top_recipient_name,
                                                COUNT(*) as times_received
                                         FROM grants g
                                         JOIN entities e_granter ON g.granter_id = e_granter.entity_id
                                         JOIN entities e_recipient ON g.recipient_id = e_recipient.entity_id
                                         WHERE e_granter.name = ?
                                         GROUP BY g.recipient_id
                                         ORDER BY times_received DESC, top_recipient_name
                                         LIMIT {NUM_TOP_RECIPIENTS};""",
                                                           (granter_name,))
            return [(name, int(num_grants)) for name, num_grants in results]
        except sqlite3.Error as e:
            self.logger.error(f"couldn't get top recipients from {granter_name!r}: {e}")
            raise

    def grant_karma(self,
                    granter_name: str,
                    recipient_name: str,
                    amount: int) -> None:
        if self.entity_mgr.get_status(recipient_name) == Status.OPTED_OUT:
            self.logger.info(
                f"{granter_name!r} can't grant {amount!r} karma to opted-out {recipient_name!r}")
            raise OptedOutRecipientError

        if self.entity_mgr.get_status(granter_name) == Status.OPTED_OUT:
            self.logger.info(
                f"opted-out {granter_name!r} can't grant {amount!r} karma to {recipient_name!r}")
            raise OptedOutGranterError

        try:
            # make an entry in the 'grants' table using subqueries to look up 'entity_id' for granter and recipient
            self.db_mgr.execute_statement("""
                                              INSERT INTO grants (granter_id, recipient_id, amount)
                                              SELECT
                                                  (SELECT entity_id FROM entities WHERE name = ?),
                                                  (SELECT entity_id FROM entities WHERE name = ?),
                                                  ?;""",
                                          (granter_name, recipient_name, amount))
            # make an entry in the 'entities' table, which tracks total karma for each user
            self.db_mgr.execute_statement("""
                                              UPDATE entities
                                              SET karma = karma + ?
                                              WHERE name = ?;""",
                                          (amount, recipient_name))
            self.logger.info(f"{granter_name!r} granted {amount!r} karma to {recipient_name!r}")
        except sqlite3.Error as e:
            self.logger.error(f"couldn't grant {amount!r} karma from {granter_name!r} to {recipient_name!r}: {e}")
            raise
