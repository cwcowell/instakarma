from constants import NUM_TOP_GRANTERS, NUM_TOP_RECIPIENTS
from db_mgr import DbMgr
from entity_mgr import EntityMgr
from exceptions import OptedOutEntityError
from enums import Status

from logging import Logger
import sqlite3


class KarmaMgr:

    # TODO: I THINK THERE ARE PLACES WHERE I PASS IN A CONN AND A DB MANAGER, BUT ONLY NEED THE LATTER

    def __init__(self,
                 db_mgr: DbMgr,
                 entity_mgr: EntityMgr,
                 logger: Logger):
        self.db_mgr = db_mgr
        self.entity_mgr = entity_mgr
        self.logger = logger

    def get_karma(self, name: str) -> int:
        try:
            self.logger.debug(f"Asking DB for karma of name '{name}'")
            results: list = self.db_mgr.execute_statement("""
                                                               SELECT karma
                                                               FROM entities
                                                               WHERE name = ? AND opt_in = TRUE;""",
                                                          (name,))
            result = results[0]
            if result:
                return result[0]
            else:
                self.logger.info(f"Name '{name}' is opted-out or doesn't exist in 'entities' table")
                raise ValueError
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't get karma for name '{name}'")
            raise e

    def get_top_granters(self, recipient_name: str) -> list[tuple[str, int]]:
        try:
            self.logger.debug(f"Asking DB for top granters to name '{recipient_name}'")
            with self.db_mgr.get_db_connection() as conn:
                results: list = self.db_mgr.execute_statement(f"""
                                                   SELECT e_granter.name as top_granter_name,
                                                          COUNT(*) as times_granted
                                                   FROM grants g
                                                   JOIN entities e_granter ON g.granter_id = e_granter.entity_id
                                                   JOIN entities e_recipient ON g.recipient_id = e_recipient.entity_id
                                                   WHERE e_recipient.name = ?
                                                   GROUP BY g.granter_id
                                                   ORDER BY times_granted DESC
                                                   LIMIT {NUM_TOP_GRANTERS};""",
                                                              (recipient_name,))
            top_granters: list[tuple[str, int]] = []
            for row in results:
                granter_name: str = row[0]
                times_granted: int = int(row[1])
                top_granters.append((granter_name, int(times_granted)))
            return top_granters
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't get biggest granters to name '{recipient_name}': {e}")
            raise e

    def get_top_recipients(self, granter_name: str) -> list[tuple[str, int]]:
        try:
            self.logger.debug(f"Asking DB for top recipients from name '{granter_name}'")
            results: list = self.db_mgr.execute_statement(f"""
                                         SELECT e_recipient.name as top_recpient_name,
                                                COUNT(*) as times_received
                                         FROM grants g
                                         JOIN entities e_granter ON g.granter_id = e_granter.entity_id
                                         JOIN entities e_recipient ON g.recipient_id = e_recipient.entity_id
                                         WHERE e_granter.name = ?
                                         GROUP BY g.recipient_id
                                         ORDER BY times_received DESC
                                         LIMIT {NUM_TOP_RECIPIENTS};""",
                                                           (granter_name,))
            top_recipients: list[tuple[str, int]] = []
            for row in results:
                recipient_name: str = row[0]
                times_granted: int = int(row[1])
                top_recipients.append((recipient_name, int(times_granted)))
            return top_recipients
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't get top recipients from name '{granter_name}': {e}")
            raise e

    def grant_karma(self,
                    granter_name: str,
                    recipient_name: str,
                    amount: int) -> None:
        if self.entity_mgr.get_status(recipient_name) == Status.OPT_OUT:
            self.logger.info(
                f"Can't grant '{amount}' karma from name '{granter_name}' to opted-out name '{recipient_name}'")
            raise OptedOutEntityError

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
            self.logger.info(f"Name '{granter_name}' granted '{amount}' karma to name '{recipient_name}'")
        except sqlite3.Error as e:
            self.logger.error(
                f"Couldn't grant '{amount}' karma from name '{granter_name}' to name '{recipient_name}': {e}")
            raise e
