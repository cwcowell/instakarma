from db_mgr import DbMgr
from entity_mgr import EntityMgr
from karma_mgr import KarmaMgr
from enums import Status
import response_blocks

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
        respond(text=f"{name} is now {new_status.value} in instakarma",
                blocks=response_blocks.change_status(new_status),
                response_type='ephemeral')

    def help(self, respond):
        respond(text="instakarma usage",
                blocks=response_blocks.help,
                response_type='ephemeral')

    def leaderboard(self, respond) -> None:
        """ Respond to Slack with a list of all non-user entities and their karma, in descending karma order. """
        try:
            results: list = self.db_mgr.execute_statement("""
                                                          SELECT name, karma 
                                                          FROM entities 
                                                          WHERE user_id IS NULL 
                                                          ORDER BY karma DESC, name;""",
                                                          ())
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't get karma of all objects: {e}")
            raise e
        leader_text: str = '\n'.join(f"• {karma} {name}" for name, karma in results)
        if not leader_text:
            leader_text = "No objects have karma"
        respond(text="show karma of objects",
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
            your_karma_text: str = "You haven't granted or received any karma yet."
            respond(text=f"instakarma stats for {name}",
                    blocks=response_blocks.my_stats(name, your_karma_text, '', ''),
                    response_type='ephemeral')
            return

        status: Status = entity_mgr.get_status(name)
        if status == Status.OPTED_OUT:
            your_karma_text: str = f"You've opted out of instakarma, so no stats are available.\n" \
                                   "Opt in with */instakarma opt-in*"
            respond(text=f"instakarma stats for {name}",
                    blocks=response_blocks.my_stats(name, your_karma_text, '', ''),
                    response_type='ephemeral')
            return

        your_karma_text: str = (f"*How much karma do I have?*\n"
                                f"You have *{karma_mgr.get_karma(name)}* karma\n")

        top_recipients_text: str = ''
        top_recipients: list[tuple[str, int]] = karma_mgr.get_top_recipients(name)
        if top_recipients:
            top_recipients_text = "*Who have I given the most karma to?*\n"
        for recipient_name, amount in top_recipients:
            top_recipients_text += f"• {str(amount)} to {recipient_name}\n"

        top_granters_text: str = ''
        top_granters: list[tuple[str, int]] = karma_mgr.get_top_granters(name)
        if top_granters:
            top_granters_text = "*Who has given me the most karma?*\n"
        for granter_name, amount in top_granters:
            top_granters_text += f"• {str(amount)} from {granter_name}\n"

        respond(text=f"instakarma stats for {name}",
                blocks=response_blocks.my_stats(name, your_karma_text, top_recipients_text, top_granters_text),
                response_type='ephemeral')
