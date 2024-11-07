from typing import Final

# db
DB_FILE_NAME: Final[str] = 'db/instakarma.db'
DB_BACKUP_FILE_NAME: Final[str] = f'{DB_FILE_NAME}.backup'
DB_DDL_FILE_NAME: Final[str] = 'db/instakarma_ddl.sql'

# instakarma-admin
GRANTS_EXPORT_FILE: Final[str] = 'grants.csv'

# logging
LOG_FILE: Final[str] = 'logs/instakarma.log'
LOG_FILE_SIZE: Final[int] = 1024 * 1024 * 10
LOG_FILE_COUNT: Final[int] = 5
LOG_LEVEL: Final[str] = 'DEBUG'
# LOG_LEVEL: Final[str] = 'INFO'
LOGGER_NAME: Final[str] = 'instakarma'

# /instakarma stats
NUM_TOP_GRANTERS: Final[int] = 5
NUM_TOP_RECIPIENTS: Final[int] = 5
