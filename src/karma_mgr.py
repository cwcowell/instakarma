from constants import NUM_TOP_GRANTERS, NUM_TOP_RECIPIENTS
from db_mgr import DbMgr
from entity_dao import EntityDao
from enums import Action, Status
from exceptions import OptedOutGranterError, OptedOutRecipientError
from string_mgr import StringMgr

from logging import Logger
import sqlite3


class KarmaMgr:
    """Handle all behavior relating to karma."""

    def __init__(self,
                 db_mgr: DbMgr,
                 entity_mgr: EntityDao,
                 logger: Logger):
        self.db_mgr = db_mgr
        self.entity_mgr = entity_mgr
        self.logger = logger

    def get_karma(self, name: str) -> int:
        """Get the current karma for any entity, whether person or object.

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
            result = results[0]
            if result:
                return result[0]
            else:
                msg: str = f"{name!r} is opted-out or doesn't exist in 'entities' table"
                self.logger.info(msg)
                raise ValueError(msg)
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('karma.get-karma.sql-error', name=name, e=e))
            raise

    def get_top_granters(self, recipient_name: str) -> list[tuple[str, int]]:
        """Get the names and amount of karma granted to a specific person by their most generous granters.

        :returns: List of tuples, where each tuple contains the name of the granter
                  and the amount of karma they've granted to the recipient
        :raises sqlite3.Error: If anything goes wrong with the DB
        """

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
            self.logger.error(StringMgr.get_string('karma.get-top-granters.sql-error',
                                                   name=recipient_name,
                                                   e=e))
            raise

    def get_top_recipients(self, granter_name: str, action: Action) -> list[tuple[str, int]]:
        """Get the names and amount of karma that the granter has been most generous to.

        :returns: List of tuples, where each tuple contains the name of the recipient
                  and the amount of karma they've received from the recipient
        :raises sqlite3.Error: If anything goes wrong with the DB
        """

        amount: int = 1 if action is Action.INCREMENT else -1
        try:
            results: list = self.db_mgr.execute_statement(f"""
                                         SELECT recipient.name as top_recipient_name,
                                                COUNT(*) as times_received
                                         FROM grants g
                                         JOIN entities granter ON g.granter_id = granter.entity_id
                                         JOIN entities recipient ON g.recipient_id = recipient.entity_id
                                         WHERE granter.name = ?
                                         AND g.amount = ?
                                         GROUP BY g.recipient_id
                                         ORDER BY times_received DESC, top_recipient_name
                                         LIMIT ?;""",
                                                          (granter_name, amount, NUM_TOP_RECIPIENTS))
            return [(name, (int(num_grants)) * amount) for name, num_grants in results]
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('karma.get-top-recipients.sql-error',
                                                   name=granter_name,
                                                   e=e))
            raise

    def grant_karma(self,
                    granter_name: str,
                    recipient_name: str,
                    amount: int) -> None:
        """Grant karma.

        :raises OptedOutGranterError: If the granter has `opted-out` status
        :raises OptedOutRecipientError: If the recipient has `opted-out` status
        :raises sqlite3.Error: If anything goes wrong with the DB
        """

        if self.entity_mgr.get_status(granter_name) == Status.OPTED_OUT:
            self.logger.info(StringMgr.get_string('karma.grant-karma.granter-opted-out',
                                                  granter_name=granter_name,
                                                  amount=amount,
                                                  recipient_name=recipient_name))
            raise OptedOutGranterError

        if self.entity_mgr.get_status(recipient_name) == Status.OPTED_OUT:
            self.logger.info(StringMgr.get_string('karma.grant-karma.recipient-opted-out',
                                                  granter_name=granter_name,
                                                  amount=amount,
                                                  recipient_name=recipient_name))
            raise OptedOutRecipientError

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
            self.logger.info(StringMgr.get_string('karma.grant-karma.granted',
                                                  granter_name=granter_name,
                                                  amount=amount,
                                                  recipient_name=recipient_name))
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('karma.grant-karma.sql-error',
                                                   granter_name=granter_name,
                                                   amount=amount,
                                                   recipient_name=recipient_name,
                                                   e=e))
            raise
