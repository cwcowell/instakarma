from typing import Final

DB_FILE: Final[str] = 'db/instakarma.db'
DB_DDL_FILE: Final[str] = 'db/instakarma_ddl.sql'

LOG_FILE: Final[str] = 'log/instakarma.log'
LOG_FILE_SIZE: Final[int] = 1024 * 1024 * 5
LOG_FILE_COUNT: Final[int] = 3

LOG_LEVEL: Final[str] = 'DEBUG'
# LOG_LEVEL: Final[str] = 'INFO'

# for use with `/instakarma stats`
NUM_TOP_GRANTERS: Final[int] = 5
NUM_TOP_RECIPIENTS: Final[int] = 5