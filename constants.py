from typing import Final

DB_FILE: Final[str] = 'db/instakarma.db'
DB_FILE_BACKUP: Final[str] = f'{DB_FILE}.backup'
DB_DDL_FILE: Final[str] = 'db/instakarma_ddl.sql'

# for use with instakarma-admin
GRANTS_EXPORT_FILE: Final[str] = 'grants.csv'

ADMIN_LOG_FILE: Final[str] = 'logs/instakarma-admin.log'
ADMIN_LOG_FILE_SIZE: Final[int] = 1024 * 1024 * 1
ADMIN_LOG_FILE_COUNT: Final[int] = 1
ADMIN_LOG_LEVEL: Final[str] = 'DEBUG'
# ADMIN_LOG_LEVEL: Final[str] = 'INFO'
ADMIN_LOGGER_NAME: Final[str] = 'instakarma-admin'

BOT_LOG_FILE: Final[str] = 'logs/instakarma-bot.log'
BOT_LOG_FILE_SIZE: Final[int] = 1024 * 1024 * 5
BOT_LOG_FILE_COUNT: Final[int] = 3
# BOT_LOG_LEVEL: Final[str] = 'DEBUG'
BOT_LOG_LEVEL: Final[str] = 'INFO'
BOT_LOGGER_NAME: Final[str] = 'instakarma-bot'

# for use with `/instakarma stats`
NUM_TOP_GRANTERS: Final[int] = 5
NUM_TOP_RECIPIENTS: Final[int] = 5

