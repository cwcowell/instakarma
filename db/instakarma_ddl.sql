-- Data definitions for SQLite 3.45

PRAGMA foreign_keys = ON; -- Weirdly required by SQLite

-- Optimizations for expected workload
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- Store current (not historical) karma for all entities
CREATE TABLE entities (
    entity_id   INTEGER  PRIMARY KEY,     -- SQLite autoincrements primary keys automatically
    entity_name TEXT     NOT NULL UNIQUE, -- a Slack username like `@foo` or anything else like `Python`
    karma       INTEGER  NOT NULL DEFAULT 0, -- this could be calculated from grants table, but is here for efficiency
    disabled    BOOLEAN  NOT NULL DEFAULT FALSE,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Log individual karma grants for auditing
CREATE TABLE grants (
    grant_id      INTEGER  PRIMARY KEY, -- SQLite autoincrements primary keys automatically
    granter_id    INTEGER  NOT NULL,
    recipient_id  INTEGER  NOT NULL,
    amount        INTEGER  NOT NULL CHECK (amount IN (-1, 1)),
    timestamp     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (granter_id) REFERENCES entities (entity_id),
    FOREIGN KEY (recipient_id) REFERENCES entities (entity_id)
);

-- Automatically creates implicit index on `entity_name` in `entities` table due to `UNIQUE` keyword