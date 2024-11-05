-- data definitions for SQLite 3.45

PRAGMA foreign_keys = ON; -- weirdly required by SQLite

PRAGMA synchronous = NORMAL; -- for testing only: slower but flushes with every commit()

-- store current (not historical) karma for all entities
CREATE TABLE entities
(
    entity_id  INTEGER PRIMARY KEY,                        -- SQLite auto-increments primary keys automatically
    name       TEXT     NOT NULL UNIQUE,                   -- Slack username like '@bob', or name of non-user entity like 'banyan'
    user_id    TEXT UNIQUE,                                -- Slack user ID; not used for non-user entities like 'banyan'
    karma      INTEGER  NOT NULL DEFAULT 0,                -- could be calculated from the 'grants' table, but is here for efficiency
    opted_in   BOOLEAN  NOT NULL DEFAULT TRUE,             -- `TRUE` means the entity is participating in instakarma
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP -- no plans for use, but might be useful in future?
);

-- store individual karma grants for auditing
CREATE TABLE grants
(
    grant_id     INTEGER PRIMARY KEY, -- SQLite auto-increments primary keys automatically
    granter_id   INTEGER  NOT NULL,
    recipient_id INTEGER  NOT NULL,
    amount       INTEGER  NOT NULL CHECK (amount IN (-1, 1)),
    timestamp    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (granter_id) REFERENCES entities (entity_id),
    FOREIGN KEY (recipient_id) REFERENCES entities (entity_id)
);

-- 'UNIQUE' keyword automatically creates indices on 'entities.name' and 'entities.user_id'