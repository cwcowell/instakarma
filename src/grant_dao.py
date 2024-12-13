from enums import Action
from entity_dao import EntityDAO
from db_mgr import DbMgr

from logging import Logger


class GrantDAO:
    # def grant_to_valid_user(self, granter_user_id: str, recipient_name: str, action: Action) -> None:

    def __init__(self, db_mgr: DbMgr, logger: Logger):
        self.db_mgr = db_mgr
        self.logger = logger


    def grant_to_object(self, granter_user_id: str, recipient_name: string, action: Action) -> str:
        """ Grant positive/negative karma to an object, not a person.

        Add recipient to DB if they don't exist already.
        If the recipient has opted-out status, don't grant karma to them.

        :param granter_user_id: user id of the person granting karma
        :param recipient_name: name of the object receiving karma
        :param action: the Action, so we know whether to increment or decrement recipient's karma
        :returns: message to send back to Slack channel
        """
        entity_dao: EntityDAO = EntityDAO(self.db_mgr, self.logger)

        granter_name: str = entity_dao.get_name_from_user_id(granter_user_id)
        recipient_name: str = recipient[0]
        action: Action = recipient[1]
        amount, verb, emoji = self.message_parser.get_amount_verb_emoji(action)
        self.entity_mgr.add_entity(recipient_name, None)
        try:
            self.karma_mgr.grant_karma(granter_name, recipient_name, amount)
            recipient_total_karma: int = self.karma_mgr.get_karma(recipient_name)
            say(f"{emoji} {recipient_name} {verb}, now has {recipient_total_karma} karma")
        except OptedOutRecipientError:
            say(StringMgr.get_string('grant.recipient-opted-out', name=recipient_name))
        except OptedOutGranterError:
            say(StringMgr.get_string('grant.granter-opted-out', name=recipient_name))

