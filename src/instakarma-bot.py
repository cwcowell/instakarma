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
from utils import ignore_channel
from utils import ignored_channel_id_to_name

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
def handle_karma_grants(message: dict, say, client) -> None:
    """Look for "++" or "--" in any message in any channel the bot is a member of.

    This is a quick check to filter out the 99% of messages that don't contain "++" or "--".

    Then more sophisticated regexes in `message_parser.py` will parse the message more carefully to figure out
    who the karma recipient(s) is, if any.

    :param message: The incoming Slack message
    :param say: any text passed to this callback function will be displayed to the user in Slack
    :param client: used to send ephemeral messages (displayed to sender only)
    """

    with bot_lock:  # don't process other messages until this one is done
        channel_id: str = message['channel']
        granter_user_id: str = message['user']
        msg_text: str = message['text']
        thread_timestamp: str | None = message.get('thread_ts', None) # set if grant occurred in a thread

        if ignore_channel(channel_id):
            logger.info("Ignored message in channel "
                        f"{ignored_channel_id_to_name(channel_id)!r}")

            client.chat_postEphemeral(channel=channel_id,
                                      user=message['user'],
                                      text="❌ instakarma is disabled in this channel",
                                      thread_ts=thread_timestamp)
            return

        # if MAINTENANCE_MODE:
        #     say(StringMgr.get_string('maintenance-mode'),
        #         thread_ts=thread_timestamp)
        #     return

        valid_user_recipients: list[tuple[str, Action]] = message_parser.detect_valid_user_recipients(msg_text)
        invalid_user_recipients: list[tuple[str, Action]] = message_parser.detect_invalid_user_recipients(msg_text)
        object_recipients: list[tuple[str, Action]] = message_parser.detect_object_recipients(msg_text)

        for recipient in valid_user_recipients:
            grant_mgr.grant_to_valid_user(say, granter_user_id, recipient, thread_timestamp)
        for recipient in invalid_user_recipients:
            grant_mgr.grant_to_invalid_user(say, granter_user_id, recipient, thread_timestamp)
        for recipient in object_recipients:
            grant_mgr.grant_to_object(say, granter_user_id, recipient, thread_timestamp)


@app.command('/instakarma')
def handle_instakarma_command(ack, respond, command) -> None:
    """Parse the `/instakarma` slash command and call the appropriate handler for the specified subcommand.

    :param ack: Slack requires us to call this callback to acknowledge receipt of the slash command
    :param respond: Any text passed to this callback function will be displayed to the user in Slack
    :param command: If the user typed `/instakarma foo` this is `foo`
    """

    with bot_lock:  # block other slash commands from processing until this one is done
        ack()  # required by Slack SDK
        thread_timestamp: str | None = command.get('thread_ts', None)  # set if command occurred in a thread, None otherwise

        if MAINTENANCE_MODE:
            respond(StringMgr.get_string('maintenance-mode'), thread_ts=thread_timestamp)
            return

        subcommand = command['text'].lower()
        match subcommand:
            case 'help' | '':
                action_mgr.help(respond)
            case 'leaderboard':
                action_mgr.leaderboard(respond)
            case 'my-stats':
                action_mgr.my_stats(command, respond, entity_mgr, karma_mgr)
            case 'opt-in':
                action_mgr.set_status(command, respond, Status.OPTED_IN, entity_mgr)
            case 'opt-out':
                action_mgr.set_status(command, respond, Status.OPTED_OUT, entity_mgr)
            case _:
                respond(StringMgr.get_string('error.invalid-slash-subcommand', subcommand=subcommand))
                action_mgr.help(respond)


@app.event("message")
def handle_message_events(body, logger):
    """Accept all messages but do nothing.

    This suppresses the console output that normally appears after every message.
    """
    with bot_lock:  # block other slash commands from processing until this one is done
        pass

if __name__ == "__main__":
    # TODO: remove unnecessary layers of error handling;
    #  Handle at error location and also at user-facing level
    SLACK_APP_TOKEN: Final[str] = (os.getenv('SLACK_APP_TOKEN') or
                                   get_secret(SLACK_APP_TOKEN_SECRET_ID))
    slack_message_handler: SocketModeHandler = SocketModeHandler(app=app,
                                                                 app_token=SLACK_APP_TOKEN)
    logger: Logger = LogMgr.get_logger(LOGGER_NAME,
                                       LOG_FILE,
                                       LOG_LEVEL,
                                       LOG_FILE_SIZE,
                                       LOG_FILE_COUNT)
    db_mgr: DbMgr = DbMgr(logger)
    slack_api_mgr: SlackApiMgr = SlackApiMgr(app, logger)
    action_mgr: ActionMgr = ActionMgr(db_mgr, logger)
    entity_mgr: EntityMgr = EntityMgr(db_mgr, logger, slack_api_mgr)
    karma_mgr: KarmaMgr = KarmaMgr(db_mgr, entity_mgr, logger)
    message_parser: MessageParser = MessageParser(logger)
    grant_mgr: GrantMgr = GrantMgr(entity_mgr, karma_mgr, logger, message_parser, db_mgr)

    db_mgr.init_db()
    bot_lock: Lock = Lock()  # bot isn't thread-safe, so prevent concurrent operations
    slack_message_handler.start()  # launch the Slack listener
