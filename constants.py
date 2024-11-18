from typing import Final

# db
DB_DDL_FILE_NAME: Final[str] = 'db/instakarma_ddl.sql'
DB_FILE_NAME: Final[str] = 'db/instakarma.db'
DB_BACKUP_FILE_NAME: Final[str] = f'{DB_FILE_NAME}.backup'

# instakarma-admin
GRANTS_EXPORT_FILE: Final[str] = 'grants.csv'

# logging
LOG_FILE: Final[str] = 'logs/instakarma.log'
LOG_FILE_SIZE: Final[int] = 1024 * 1024 * 10  # 10MB
LOG_FILE_COUNT: Final[int] = 5
LOG_LEVEL: Final[str] = 'INFO'
LOGGER_NAME: Final[str] = 'instakarma'

# /instakarma stats
NUM_TOP_GRANTERS: Final[int] = 5
NUM_TOP_RECIPIENTS: Final[int] = 5
