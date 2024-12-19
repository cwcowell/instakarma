from constants import GRANTS_EXPORT_FILE
from db_mgr import DbMgr
from entity_mgr import EntityMgr
from enums import Action
from exceptions import OptedOutRecipientError, OptedOutGranterError
from karma_mgr import KarmaMgr
from message_parser import MessageParser
from string_mgr import StringMgr

from logging import Logger
from pathlib import Path
import sqlite3
import sys
from typing import Final

from slack_sdk.errors import SlackApiError


class GrantMgr:
    """Handle all behavior relating to the granting of karma."""

    def __init__(self,
                 entity_mgr: EntityMgr,
                 karma_mgr: KarmaMgr,
                 logger: Logger,
                 message_parser: MessageParser,
                 db_mgr: DbMgr):
        self.db_mgr = db_mgr
        self.entity_mgr = entity_mgr
        self.karma_mgr = karma_mgr
        self.logger = logger
        self.message_parser = message_parser

    def grant_to_valid_user(self,
                            say,
                            granter_user_id: str,
                            recipient: tuple[str, Action],
                            thread_ts: str | None = None) -> None:
        """Grant positive karma to a person already registered in Slack.

        Add granter and/or recipient to DB if they don't exist already.
        Disallow grants of karma to yourself.
        If the recipient has opted-out status, don't grant karma to them.

        :param say: Any text passed to this callback will be displayed to the user in Slack
        :param granter_user_id: User ID of the person granting karma
        :param recipient: Tuple containing the name of the recipient and the Action
                          (so we know whether to increment or decrement the recipient's karma)
        """

        recipient_user_id: str = recipient[0]
        action: Action = recipient[1]
        amount, verb, emoji = self.message_parser.get_amount_verb_emoji(action)

        try:
            granter_name: str = self.entity_mgr.get_name_from_user_id(granter_user_id)
        except SlackApiError:
            self.logger.error(StringMgr.get_string('grant.log.error.no-name-for-user-id',
                                                   user_id=granter_user_id))
            return
        try:
            recipient_name: str = self.entity_mgr.get_name_from_user_id(recipient_user_id)
        except SlackApiError:
            self.logger.error(StringMgr.get_string('grant.log.error.no-name-for-user-id',
                                                   user_id=recipient_user_id))
            return

        if action == Action.DECREMENT:
            self.logger.info(StringMgr.get_string('grant.log.info.remove-karma-from-person',
                                                  granter_name=granter_name,
                                                  recipient_name=recipient_name))
            say(StringMgr.get_string('grant.remove-karma-from-person'), thread_ts=thread_ts)
            return

        if recipient_name == granter_name:
            self.logger.info(StringMgr.get_string('grant.log.info.self-grant',
                                                  granter_name=granter_name,
                                                  amount=amount))
            say(StringMgr.get_string('grant.self-grant'), thread_ts=thread_ts)
            return

        try:
            self.karma_mgr.grant_karma(granter_name, recipient_name, amount)
        except OptedOutRecipientError:
            say(StringMgr.get_string('grant.recipient-opted-out', name=recipient_name))
            return
        except OptedOutGranterError:
            say(StringMgr.get_string('grant.granter-opted-out'))
            return
        recipient_total_karma: int = self.karma_mgr.get_karma(recipient_name)
        say(StringMgr.get_string('grant.success',
                                 emoji=emoji,
                                 recipient_name=recipient_name,
                                 verb=verb,
                                 recipient_total_karma=recipient_total_karma),
            thread_ts=thread_ts)

    def grant_to_invalid_user(self,
                              say: callable,
                              granter_user_id: str,
                              recipient: tuple[str, Action],
                              thread_ts: str | None = None) -> None:
        """Respond to Slack channel saying it can't grant karma to a user that Slack doesn't recognize.

        :param say: Any text passed to this callback will be displayed to the user in Slack
        :param granter_user_id: User ID of the person granting karma
        :param recipient: Tuple containing the name of the recipient and the Action
                          (so we know whether to increment or decrement the recipient's karma)
        """

        try:
            granter_name: str = self.entity_mgr.get_name_from_user_id(granter_user_id)
        except SlackApiError:
            self.logger.error(StringMgr.get_string('grant.log.error.no-name-for-user-id',
                                                   user_id=granter_user_id))
            return

        recipient_name: str = recipient[0]
        action: Action = recipient[1]
        amount, _, _ = self.message_parser.get_amount_verb_emoji(action)
        self.logger.info(StringMgr.get_string('grant.log.info.invalid-person',
                                              granter_name=granter_name,
                                              amount=amount,
                                              recipient_name=recipient_name))
        say(StringMgr.get_string('grant.invalid-person', recipient_name=recipient_name), 
            thread_ts=thread_ts)

    def grant_to_object(self,
                        say,
                        granter_user_id,
                        recipient,
                        thread_ts: str | None = None) -> None:
        """ Grant positive/negative karma to an object, not a person.

        Add recipient to DB if they don't exist already.
        If the recipient has opted-out status, don't grant karma to them.

        :param say: Any text passed to this callback will be displayed to the user in Slack
        :param granter_user_id: User ID of the person granting karma
        :param recipient: Tuple containing the name of the recipient and the Action
                          (so we know whether to increment or decrement the recipient's karma)
        """

        granter_name: str = self.entity_mgr.get_name_from_user_id(granter_user_id)
        recipient_name: str = recipient[0]
        action: Action = recipient[1]
        amount, verb, emoji = self.message_parser.get_amount_verb_emoji(action)
        self.entity_mgr.add_entity(recipient_name, None)
        try:
            self.karma_mgr.grant_karma(granter_name, recipient_name, amount)
            recipient_total_karma: int = self.karma_mgr.get_karma(recipient_name)
            say(f"{emoji} {recipient_name} {verb}, now has {recipient_total_karma} karma",
                thread_ts=thread_ts)
        except OptedOutRecipientError:
            say(StringMgr.get_string('grant.recipient-opted-out', name=recipient_name),
                thread_ts=thread_ts)
        except OptedOutGranterError:
            say(StringMgr.get_string('grant.granter-opted-out', name=recipient_name),
                thread_ts=thread_ts)

    def export_grants(self) -> None:
        """ Dump a history of all grants that are in the DB into a local CSV file.

        Since this is designed to be called only from `instakarma-admin`:
            * Exit rather than raise an error if anything goes wrong
            * Print messages instead of logging them

        :raises SystemExit: If anything goes wrong
        """

        grants_export_file_path: Final[Path] = Path(GRANTS_EXPORT_FILE)
        if grants_export_file_path.exists():
            sys.exit(StringMgr.get_string('grant.log.error.export-file-exists',
                                          grants_export_file_path=grants_export_file_path.resolve()))
        try:
            results: list = self.db_mgr.execute_statement(
                """
                SELECT r.name AS recipient_name,
                       g.name AS granter_name,
                       gr.amount,
                       gr.timestamp
                FROM grants gr
                JOIN entities r on gr.recipient_id = r.entity_id
                JOIN entities g on gr.granter_id = g.entity_id
                ORDER BY gr.timestamp;""",
                ())
        except sqlite3.Error as e:
            sys.exit(f"error: {e}")
        try:
            with open(grants_export_file_path, 'w') as file:
                file.write('TIMESTAMP,GRANTER,AMOUNT,RECIPIENT\n')
                for recipient_name, granter_name, delta, timestamp in results:
                    file.write(f"{timestamp},{granter_name},{delta},{recipient_name}\n")
        except Exception as e:
            sys.exit(StringMgr.get_string('grants.log.error.write-file',
                                          grants_export_file_path=grants_export_file_path.resolve(),
                                          e=e))
        print(StringMgr.get_string('grant.grants-exported',
                                   grants_export_file_path=grants_export_file_path.resolve()))
