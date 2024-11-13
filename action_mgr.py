from db_mgr import DbMgr
from entity_mgr import EntityMgr
from karma_mgr import KarmaMgr
from enums import Action, Status
import response_blocks
from string_mgr import StringMgr

from logging import Logger
import sqlite3



class ActionMgr:

    def __init__(self, db_mgr: DbMgr, logger: Logger):
        self.db_mgr = db_mgr
        self.logger = logger

    def set_status(self,
                   command: dict,
                   respond,
                   new_status: Status,
                   entity_mgr: EntityMgr) -> None:
        """ Set an entity's status to either `opted-in` or `opted-out`. """
        name: str = '@' + command['user_name']
        entity_mgr.set_status(name, new_status)
        respond(text=StringMgr.get_string('action.set-status.respond-text', name=name, status=new_status.value),
                blocks=response_blocks.change_status(new_status),
                response_type='ephemeral')

    def help(self, respond):
        respond(text=StringMgr.get_string('action.help.respond-text'),
                blocks=response_blocks.help,
                response_type='ephemeral')

    def leaderboard(self, respond) -> None:
        """ Respond to Slack with a list of all non-user entities and their karma, in descending karma order. """
        try:
            results: list = self.db_mgr.execute_statement("""
                                                          SELECT name, karma
                                                          FROM entities
                                                          WHERE user_id IS NULL
                                                          AND karma IS NOT 0
                                                          ORDER BY karma DESC, name;""",
                                                          ())
        except sqlite3.Error as e:
            self.logger.error(StringMgr.get_string('action.leaderboard.sqlite3error', e=e))
            raise
        leader_text: str = '\n'.join(f"• {karma} {name}" for name, karma in results)
        if not leader_text:
            leader_text = StringMgr.get_string('action.leaderboard.leader-text-when-no-karma')
        respond(text=StringMgr.get_string('action.leaderboard.respond-text'),
                blocks=response_blocks.leaderboard(leader_text),
                response_type="ephemeral")

    def my_stats(self,
                 command: dict,
                 respond,
                 entity_mgr: EntityMgr,
                 karma_mgr: KarmaMgr) -> None:
        """ Respond to Slack with how much karma the user has, who they've given the most karma to,
        and who has given them the most karma.

        If the user has opted out, don't display any stats.
        """
        name: str = '@' + command['user_name']

        if not entity_mgr.name_exists_in_db(name):
            your_karma_text: str = StringMgr.get_string('action.my-stats.your-karma-text-when-user-not-in-db')
            respond(text=StringMgr.get_string('action.my-stats.respond-text', name=name),
                    blocks=response_blocks.my_stats(name, your_karma_text, '', '', ''),
                    response_type='ephemeral')
            return

        status: Status = entity_mgr.get_status(name)
        if status == Status.OPTED_OUT:
            your_karma_text: str = StringMgr.get_string('action.my-stats.opted-out') + "\n" + \
                                   StringMgr.get_string('action.my-stats.opt-in-instructions')
            respond(text=StringMgr.get_string('action.my-stats.respond-text', name=name),
                    blocks=response_blocks.my_stats(name, your_karma_text, '', '', ''),
                    response_type='ephemeral')
            return

        your_karma_text: str = StringMgr.get_string('action.my-stats.my-karma-header') + "\n" + \
                               StringMgr.get_string('action.my-stats.my-karma',
                                                    amount=karma_mgr.get_karma(name)) + "\n"

        top_positive_recipients: list[tuple[str, int]] = karma_mgr.get_top_recipients(name, Action.INCREMENT)
        top_positive_recipients_text: str = StringMgr.get_string('action.my-stats.top-positive-recipients-header') + "\n"
        if not top_positive_recipients:
            top_positive_recipients_text += StringMgr.get_string('action.my-stats.top-positive-recipients-none') + "\n"
        else:
            for recipient_name, amount in top_positive_recipients:
                top_positive_recipients_text += StringMgr.get_string('action.my-stats.top-recipient',
                                                          amount=str(amount),
                                                          recipient_name=recipient_name) + '\n'

        top_negative_recipients: list[tuple[str, int]] = karma_mgr.get_top_recipients(name, Action.DECREMENT)
        top_negative_recipients_text: str = StringMgr.get_string('action.my-stats.top-negative-recipients-header') + "\n"
        if not top_negative_recipients:
            top_negative_recipients_text += StringMgr.get_string('action.my-stats.top-negative-recipients-none') + '\n'
        else:
            for recipient_name, amount in top_negative_recipients:
                top_negative_recipients_text += StringMgr.get_string('action.my-stats.top-recipient',
                                                          amount=str(amount),
                                                          recipient_name=recipient_name) + "\n"

        top_granters: list[tuple[str, int]] = karma_mgr.get_top_granters(name)
        top_granters_text = StringMgr.get_string('action.my-stats.top-granters-header') + "\n"
        if not top_granters:
            top_granters_text += StringMgr.get_string('action.my-stats.top-granters-none') + "\n"
        else:
            for granter_name, amount in top_granters:
                top_granters_text += StringMgr.get_string('action.my-stats.top-granter',
                                                          amount=str(amount),
                                                          granter_name=granter_name) + "\n"

        respond(text=StringMgr.get_string('action.my-stats.respond-text', name=name),
                blocks=response_blocks.my_stats(name,
                                                your_karma_text,
                                                top_positive_recipients_text,
                                                top_negative_recipients_text,
                                                top_granters_text),
                response_type='ephemeral')
