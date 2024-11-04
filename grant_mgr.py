from constants import GRANTS_EXPORT_FILE
from db_mgr import DbMgr
from enums import Action
from entity_mgr import EntityMgr
from exceptions import OptedOutEntityError
from karma_mgr import KarmaMgr
from message_parser import MessageParser

from logging import Logger
import sqlite3
import sys


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

        granter_name: str = self.entity_mgr.get_name_from_user_id(granter_user_id)
        recipient_name: str = self.entity_mgr.get_name_from_user_id(recipient_user_id)

        if action == Action.DECREMENT:
            self.logger.info(f"{granter_name!r} tried to reduce karma of a person with name {recipient_name!r}")
            say(':x: Sorry, you can only remove karma from things (like python), not people (like @elvis)')
            return

        if recipient_name == granter_name:
            self.logger.info(f"{granter_name!r} tried to self-grant {amount} karma")
            say(f":x: Sorry, you can't grant positive or negative karma to yourself")
            return

        try:
            self.karma_mgr.grant_karma(granter_name, recipient_name, amount)
        except OptedOutEntityError:
            self.logger.info(f"{granter_name!r} tried to grant karma to opted-out entity {recipient_name!r}'")
            say(f":x: Sorry, {recipient_name} isn't participating in Instakarma")
            return
        recipient_total_karma: int = self.karma_mgr.get_karma(recipient_name)
        say(f"{emoji} <{recipient_name}> {verb}, now has {recipient_total_karma} karma")

    def grant_to_invalid_user(self,
                              say,
                              granter_user_id,
                              recipient) -> None:
        """ Respond to Slack channel saying it can't grant karma to a user who isn't recognized by Slack. """
        granter_name: str = self.entity_mgr.get_name_from_user_id(granter_user_id)
        recipient_name: str = recipient[0]
        action: Action = recipient[1]
        amount, _, _ = self.message_parser.get_amount_verb_emoji(action)
        self.logger.info(f"{granter_name!r} tried to grant {amount!r} karma "
                         f"to unrecognized name {recipient_name!r}")
        say(f":x: Sorry, I don't recognize the user {recipient_name}")

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
        except OptedOutEntityError:
            self.logger.info(f"{granter_name!r} can't grant karma to opted-out entity {recipient_name!r}")
            say(f":x: Sorry, {recipient_name} is not participating in Instakarma")

    def export_grant_history(self) -> None:
        """ Dump a history of all grants that are in the DB into a local CSV file.

        Exit rather than raise an error if anything goes wrong, since this is only called from instabase-admin.
        Print rather than log messages for the same reason.
        """
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
            sys.exit(f"Error when retrieving all grants: {e}")

        with open(GRANTS_EXPORT_FILE, 'w') as file:
            file.write('TIMESTAMP,GRANTER,AMOUNT,RECIPIENT\n')
            for recipient_name, granter_name, delta, timestamp in results:
                file.write(f"{timestamp},{granter_name},{delta},{recipient_name}\n")
        print(f"All grants exported as CSV to {GRANTS_EXPORT_FILE}")
