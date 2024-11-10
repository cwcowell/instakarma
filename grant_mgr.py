from constants import GRANTS_EXPORT_FILE
from db_mgr import DbMgr
from enums import Action
from entity_mgr import EntityMgr
from exceptions import OptedOutRecipientError, OptedOutGranterError
from karma_mgr import KarmaMgr
from message_parser import MessageParser

from logging import Logger
from pathlib import Path
import sqlite3
import sys
from typing import Final

from slack_sdk.errors import SlackApiError

from string_mgr import StringMgr


class GrantMgr:

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
                            recipient: tuple[str, Action]) -> None:
        """ Grant positive karma to a person already registered in Slack.

        Add granter and/or recipient to DB if they don't exist already.
        Disallow grants of karma to yourself.
        If the recipient has opted-out status, don't grant karma to them.
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
            say(StringMgr.get_string('grant.remove-karma-from-person'))
            return

        if recipient_name == granter_name:
            self.logger.info(StringMgr.get_string('grant.log.info.self-grant',
                                                  granter_name=granter_name,
                                                  amount=amount))
            say(StringMgr.get_string('grant.self-grant'))
            return

        try:
            self.karma_mgr.grant_karma(granter_name, recipient_name, amount)
        except OptedOutRecipientError:
            say(f":x: sorry, {recipient_name} has opted out of instakarma")
            return
        except OptedOutGranterError:
            say(f":x: sorry, you can't grant karma because you've opted out of instakarma\n"
                "opt in with */instakarma opt-in*")
            return
        recipient_total_karma: int = self.karma_mgr.get_karma(recipient_name)
        say(f"{emoji} <{recipient_name}> {verb}, now has {recipient_total_karma} karma")

    def grant_to_invalid_user(self,
                              say: callable,
                              granter_user_id: str,
                              recipient: tuple[str, Action]) -> None:
        """ Respond to Slack channel saying it can't grant karma to a user who Slack doesn't recognize. """
        try:
            granter_name: str = self.entity_mgr.get_name_from_user_id(granter_user_id)
        except SlackApiError:
            self.logger.error("Couldn't grant karma because couldn't get name for "
                              f"granter user_id {granter_user_id!r}")
            return

        recipient_name: str = recipient[0]
        action: Action = recipient[1]
        amount, _, _ = self.message_parser.get_amount_verb_emoji(action)
        self.logger.info(f"{granter_name!r} tried to grant {amount!r} karma "
                         f"to invalid person {recipient_name!r}")
        say(f":x: sorry, user {recipient_name} isn't registered in Slack")

    def grant_to_object(self,
                        say,
                        granter_user_id,
                        recipient) -> None:
        """ Grant positive/negative karma to an object, not a person.

        Add recipient to DB if they don't exist already.
        If the recipient has opted-out status, don't grant karma to them.
        """
        granter_name: str = self.entity_mgr.get_name_from_user_id(granter_user_id)
        recipient_name: str = recipient[0]
        action: Action = recipient[1]
        amount, verb, emoji = self.message_parser.get_amount_verb_emoji(action)
        self.entity_mgr.add_entity(recipient_name, None)
        try:
            self.karma_mgr.grant_karma(granter_name, recipient_name, amount)
            recipient_total_karma: int = self.karma_mgr.get_karma(recipient_name)
            say(f"{emoji} {recipient_name} {verb}, now has {recipient_total_karma} karma")
        except OptedOutRecipientError:
            say(f":x: sorry, {recipient_name} has opted out of instakarma")
        except OptedOutGranterError:
            say(f":x: sorry, you can't grant karma because you've opted out of instakarma\n"
                "opt in with */instakarma opt-in*")

    def export_grants(self) -> None:
        """ Dump a history of all grants that are in the DB into a local CSV file.

        Since this is designed to be called from `instakarma-admin` only:

        * Exit rather than raise an error if anything goes wrong
        * Print messages instead of logging them
        """
        grants_export_file_path: Final[Path] = Path(GRANTS_EXPORT_FILE)
        if grants_export_file_path.exists():
            sys.exit(f"aborted export because {grants_export_file_path.name!r} already exists")

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
            sys.exit(f"error writing to {grants_export_file_path.name!r}: {e}")
        print(f"all grants exported as CSV to {grants_export_file_path.name!r}")
