import os

# Run this before imports. If this script is run from the wrong place, some imports fail.
if os.path.basename(os.getcwd()) != 'src':
    raise SystemExit("Error: 'instakarma-bot' must be run from the '<REPO-ROOT-DIR>/src/' directory")

from action_mgr import ActionMgr
from constants import *
from db_mgr import DbMgr
from enums import *
from entity_mgr import EntityMgr
from grant_mgr import GrantMgr
from karma_mgr import KarmaMgr
from log_mgr import LogMgr
from message_parser import MessageParser
from slack_api_mgr import SlackApiMgr
from string_mgr import StringMgr

from logging import Logger
import traceback
from threading import Lock

import boto3
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


def get_secret(secret_id: str) -> str:
    """Get secret from AWS Secrets Manager.

    :returns str: Decrypted secret string
    :raises SystemExit: If there are errors retrieving the secret
    """
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=AWS_REGION)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_id)
    except Exception as e:
        raise SystemExit(f"Error retrieving secret with id {secret_id!r} from AWS Secret Manager: {e}\n" +
                 traceback.format_exc())
    return get_secret_value_response['SecretString']

SLACK_BOT_TOKEN: Final[str] = (os.getenv('SLACK_BOT_TOKEN') or
                               get_secret(SLACK_BOT_TOKEN_SECRET_ID))
app: App = App(token=SLACK_BOT_TOKEN)


@app.message(r'(\+\+|--)')
def handle_karma_grants(message: dict, say) -> None:
    """Look for "++" or "--" in any message in any channel the bot is a member of.

    This is a quick check to filter out the 99% of messages that don't contain "++" or "--".

    Then more sophisticated regexes in `message_parser.py` will parse the message more carefully to figure out
    who the karma recipient(s) is, if any.

    :param message: The incoming Slack message
    :param say: any text passed to this callback function will be displayed to the user in Slack
    """

    with bot_lock:  # block other slash commands from processing until this one is done
        if message['channel'] in ignored_channel_ids:
            logger.info(f"Ignored message in channel {message['channel']!r}")
            return

        granter_user_id: str = message['user']
        msg_text: str = message['text']
        # capture the timestamp if grant occurred in a thread, None otherwise
        thread_timestamp: str | None = message.get('thread_ts', None)

        if MAINTENANCE_MODE:
            say(StringMgr.get_string('maintenance-mode'), thread_ts=thread_timestamp)
            return

        valid_user_recipients: list[tuple[str, Action]] = message_parser.detect_valid_user_recipients(msg_text)
        invalid_user_recipients: list[tuple[str, Action]] = message_parser.detect_invalid_user_recipients(msg_text)
        object_recipients: list[tuple[str, Action]] = message_parser.detect_object_recipients(msg_text)

        for recipient in valid_user_recipients:
            grant_handler.grant_to_valid_user(say, granter_user_id, recipient, thread_timestamp)
        for recipient in invalid_user_recipients:
            grant_handler.grant_to_invalid_user(say, granter_user_id, recipient, thread_timestamp)
        for recipient in object_recipients:
            grant_handler.grant_to_object(say, granter_user_id, recipient, thread_timestamp)


@app.command('/instakarma')
def handle_instakarma_command(ack, respond, command) -> None:
    """Parse the `/instakarma` slash command and call the appropriate handler for the specified subcommand.

    :param ack: Slack requires us to call this callback to acknowledge receipt of the slash command
    :param respond: Any text passed to this callback function will be displayed to the user in Slack
    :param command: If the user typed `/instakarma foo` this is `foo`
    """

    with bot_lock:  # block other slash commands from processing until this one is done
        ack()  # required by Slack SDK
        thread_ts: str | None = command.get('thread_ts', None)  # set if command occurred in a thread, None otherwise

        if MAINTENANCE_MODE:
            respond(StringMgr.get_string('maintenance-mode'), thread_ts=thread_ts)
            return

        subcommand = command['text'].lower()
        match subcommand:
            case 'help' | '':
                action_manager.help(respond)
            case 'leaderboard':
                action_manager.leaderboard(respond)
            case 'my-stats':
                action_manager.my_stats(command, respond, entity_manager, karma_manager)
            case 'opt-in':
                action_manager.set_status(command, respond, Status.OPTED_IN, entity_manager)
            case 'opt-out':
                action_manager.set_status(command, respond, Status.OPTED_OUT, entity_manager)
            case _:
                respond(StringMgr.get_string('error.invalid-slash-subcommand', subcommand=subcommand))
                action_manager.help(respond)


@app.event("message")
def handle_message_events(body, logger):
    """Accept all messages but do nothing.

    This suppresses the console output that normally appears after every message.
    """
    with bot_lock:  # block other slash commands from processing until this one is done
        pass

if __name__ == "__main__":
    # TODO: remove unnecessary layers of error handling. Handle at error location and also at user-facing level
    SLACK_APP_TOKEN: Final[str] = (os.getenv('SLACK_APP_TOKEN') or
                                   get_secret(SLACK_APP_TOKEN_SECRET_ID))
    slack_message_handler: SocketModeHandler = SocketModeHandler(app=app,
                                                                 app_token=SLACK_APP_TOKEN)
    logger: Logger = LogMgr.get_logger(LOGGER_NAME,
                                       LOG_FILE,
                                       LOG_LEVEL,
                                       LOG_FILE_SIZE,
                                       LOG_FILE_COUNT)
    db_manager: DbMgr = DbMgr(logger)
    slack_api_manager: SlackApiMgr = SlackApiMgr(app, logger)
    action_manager: ActionMgr = ActionMgr(db_manager, logger)
    entity_manager: EntityMgr = EntityMgr(db_manager, logger, slack_api_manager)
    karma_manager: KarmaMgr = KarmaMgr(db_manager, entity_manager, logger)
    message_parser: MessageParser = MessageParser(logger)
    grant_handler: GrantMgr = GrantMgr(entity_manager, karma_manager, logger, message_parser, db_manager)

    db_manager.init_db()
    bot_lock: Lock = Lock()  # bot isn't thread-safe, so prevent concurrent operations
    ignored_channel_ids: list[str] = slack_api_manager.gather_ignored_channel_ids(app)

    slack_message_handler.start()  # launch the Slack listener
