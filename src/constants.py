from typing import Final

"""Collect all instakarma-related constants in one file for easy editing."""

# for AWS operations
AWS_REGION: Final[str] = 'us-east-2'

# for db operations
DB_DDL_FILE_NAME: Final[str] = '../db/instakarma_ddl.sql'
DB_FILE_NAME: Final[str] = '../db/instakarma.db'
DB_BACKUP_FILE_NAME: Final[str] = f'{DB_FILE_NAME}.backup'

# for `instakarma-admin`
GRANTS_EXPORT_FILE: Final[str] = 'grants.csv'

# for `instakarma-bot`
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
