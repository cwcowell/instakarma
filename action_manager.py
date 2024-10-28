from db_manager import DbManager
from entity_manager import EntityManager
from karma_manager import KarmaManager
from enums import Status
import response_blocks

from logging import Logger
import sqlite3


class ActionManager:

    def __init__(self, db_manager: DbManager, logger: Logger):
        self.db_manager = db_manager
        self.logger = logger

    def change_status(self,
                      command: dict,
                      respond,
                      new_status: Status,
                      entity_manager: EntityManager):
        name: str = '@' + command['user_name']
        entity_manager.change_user_status(name, new_status)
        respond(text=f"{name} is now {new_status.value} in instakarma",
                blocks=response_blocks.change_status(new_status),
                response_type='ephemeral')

    def help(self, respond):
        respond(text="instakarma usage",
                blocks=response_blocks.help,
                response_type='ephemeral')

    def leaderboard(self, respond, db_manager: DbManager):
        leader_text: str = ''
        try:
            cursor = self.db_manager.execute_statement("""
                                                       SELECT name, karma 
                                                       FROM entities 
                                                       WHERE user_id IS NULL 
                                                       ORDER BY karma DESC;""",
                                                       ())
        except sqlite3.Error as e:
            self.logger.error(f"Couldn't get karma of all objects: {e}")
            raise e
        results = cursor.fetchall()
        for result in results:
            name: str = result[0]
            karma: int = result[1]
            leader_text += f"• {karma} {name}\n"
        respond(text="show karma of objects",
                blocks=response_blocks.leaderboard(leader_text),
                response_type="ephemeral")

    def my_stats(self,
                 command: dict,
                 respond,
                 entity_manager: EntityManager,
                 karma_manager: KarmaManager):
        name: str = '@' + command['user_name']

        status: Status = entity_manager.get_status(name)
        if status == Status.OPT_OUT:
            your_karma_text: str = f"You've opted out of instakarma, so no stats are available.\n" \
                                   "Opt in with */instakarma opt-in"
            respond(text=f"instakarma stats for {name}",
                        blocks=response_blocks.my_stats(name, your_karma_text, '', ''),
                        response_type='ephemeral')
            return

        your_karma_text: str = (f"*How much karma do I have?*\n"
                                f"You have *{karma_manager.get_karma(name)}* karma\n")

        top_recipients_text: str = ''
        top_recipients: list[tuple[str, int]] = karma_manager.get_top_recipients(name)
        if top_recipients:
            top_recipients_text = "*Who have I given the most karma to?*\n"
        for recipient in top_recipients:
            top_recipients_text += f"• {str(recipient[1])} to {recipient[0]}\n"

        top_granters_text: str = ''
        top_granters: list[tuple[str, int]] = karma_manager.get_top_granters(name)
        if top_granters:
            top_granters_text = "*Who has given me the most karma?*\n"
        for granter in top_granters:
            top_granters_text += f"• {str(granter[1])} from {granter[0]}\n"

        respond(text=f"instakarma stats for {name}",
                blocks=response_blocks.my_stats(name, your_karma_text, top_recipients_text, top_granters_text),
                response_type='ephemeral')
