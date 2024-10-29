from enums import Action
from entity_manager import EntityManager
from exceptions import OptedOutEntityError
from karma_manager import KarmaManager
from message_parser import MessageParser

from logging import Logger


class GrantHandler():

    def __init__(self,
                 entity_manager: EntityManager,
                 karma_manager: KarmaManager,
                 logger: Logger,
                 message_parser: MessageParser):
        self.entity_manager = entity_manager
        self.karma_manager = karma_manager
        self.logger = logger
        self.message_parser = message_parser

    def grant_to_valid_user(self, say, granter_user_id: str, recipient: tuple[str, Action]):
        recipient_user_id: str = recipient[0]
        action: Action = recipient[1]
        amount, verb, emoji = self.message_parser.get_amount_verb_emoji(recipient)

        granter_name: str = self.entity_manager.get_name_from_user_id(granter_user_id)
        recipient_name: str = self.entity_manager.get_name_from_user_id(recipient_user_id)

        if action == Action.DECREMENT:
            self.logger.info(f"'{granter_name}' tried to reduce karma of a person with name '{recipient_name}'")
            say(':x: Sorry, you can only remove karma from things, not people\n*foo--* is OK\n*@foo--* is not')
            return

        if recipient_name == granter_name:
            self.logger.info(f"'{granter_name}' tried to self-grant {amount} karma")
            say(f":x: Sorry, you can't self-grant karma")
            return

        try:
            self.karma_manager.grant_karma(granter_name, recipient_name, amount)
        except OptedOutEntityError:
            self.logger.info(f"'{granter_name}' tried to grant karma to opted-out entity '{recipient_name}'")
            say(f":x: Sorry, {recipient_name} isn't participating in Instakarma")
            return
        recipient_total_karma: int = self.karma_manager.get_karma(recipient_name)
        say(f"{emoji} <{recipient_name}> {verb}, now has {recipient_total_karma} karma")

    def grant_to_invalid_user(self, say, granter_user_id, recipient):
        granter_name: str = self.entity_manager.get_name_from_user_id(granter_user_id)
        recipient_name: str = recipient[0]
        amount, _, _ = self.message_parser.get_amount_verb_emoji(recipient)
        self.logger.info(f"'{granter_name}' tried to grant '{amount}' karma "
                         f"to unrecognized name '{recipient_name}'")
        say(f":x: Sorry, I don't recognize the user {recipient_name}")

    def grant_to_object(self, say, granter_user_id, recipient):
        granter_name: str = self.entity_manager.get_name_from_user_id(granter_user_id)
        recipient_name: str = recipient[0]
        amount, verb, emoji = self.message_parser.get_amount_verb_emoji(recipient)
        self.entity_manager.add_entity(recipient_name, None)
        try:
            self.karma_manager.grant_karma(granter_name, recipient_name, amount)
            recipient_total_karma: int = self.karma_manager.get_karma(recipient_name)
            say(f"{emoji} {recipient_name} {verb}, now has {recipient_total_karma} karma")
        except OptedOutEntityError:
            self.logger.info(f"'{granter_name}' can't grant karma to opted-out entity '{recipient_name}'")
            say(f":x: Sorry, {recipient_name} is not participating in Instakarma")
