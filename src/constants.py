from channel import Channel
from enums import Environment

from typing import Final

"""Collect all instakarma-related constants in one file for easy editing."""

# which Slack instance this bot should connect to
ENVIRONMENT: Final[Environment] = Environment.PROD
# ENVIRONMENT: Final[Environment] = Environment.SANDBOX

# for AWS operations
AWS_REGION: Final[str] = 'us-east-2'
SLACK_APP_TOKEN_SECRET_ID: Final[str] = f'instakarma/{ENVIRONMENT.value}_SLACK_APP_TOKEN'
SLACK_BOT_TOKEN_SECRET_ID: Final[str] = f'instakarma/{ENVIRONMENT.value}_SLACK_BOT_TOKEN'

# for db operations
DB_DDL_FILE_NAME: Final[str] = '../db/instakarma_ddl.sql'
DB_FILE_NAME: Final[str] = '../db/instakarma.db'
DB_BACKUP_FILE_NAME: Final[str] = f'{DB_FILE_NAME}.backup'

# for `instakarma-admin`
GRANTS_EXPORT_FILE: Final[str] = 'grants.csv'

# for `instakarma-bot`

# instakarma won't respond to messages in these channels
# find channel ID by right-clicking channel in Slack and selecting *View channel details*
if ENVIRONMENT == Environment.PROD:
    IGNORED_CHANNELS: Final[list[Channel]] = [Channel(name='discuss-general', id='C06FA5MBN')]
else:
    IGNORED_CHANNELS: Final[list[Channel]] = [Channel(name='mushrooms', id='C080AKZJBH7'),
                                              Channel(name='cats', id='C07SHR3JBQD')]

LOG_FILE: Final[str] = '../logs/instakarma.log'
LOG_FILE_SIZE: Final[int] = 1024 * 1024 * 10  # 10MB
LOG_FILE_COUNT: Final[int] = 5
LOG_LEVEL: Final[str] = 'INFO'
LOGGER_NAME: Final[str] = 'instakarma'

# for `/instakarma my-stats`
NUM_TOP_GRANTERS: Final[int] = 5
NUM_TOP_RECIPIENTS: Final[int] = 5

# for StringMgr
STRINGS_FILE: Final[str] = 'strings.yml'
STRING_PLACEHOLDER: Final[str] = 'PLACEHOLDER_UI_STRING'  # return this if the key isn't in the map
