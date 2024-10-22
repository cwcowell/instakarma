-- data definitions for SQLite 3.45

PRAGMA foreign_keys = ON; -- weirdly required by SQLite

-- store current (not historical) karma for all entities
CREATE TABLE entities
(
    entity_id  INTEGER PRIMARY KEY,                        -- SQLite autoincrements primary keys automatically
    name       TEXT     NOT NULL UNIQUE,                   -- Slack username like '@bob', or name of non-user entity like 'banyan'
    user_id    TEXT UNIQUE,                                -- Slack user ID; not used for non-user entities like 'banyan'
    karma      INTEGER  NOT NULL DEFAULT 0,                -- could be calculated from grants table, but is here for efficiency
    disabled   BOOLEAN  NOT NULL DEFAULT FALSE,            -- 'true' means entity doesn't want to participate in instakarma
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP -- no plans for use, but might be useful in future?
);

-- log individual karma grants for auditing
CREATE TABLE grants
(
    grant_id     INTEGER PRIMARY KEY, -- SQLite autoincrements primary keys automatically
    granter_id   INTEGER  NOT NULL,
    recipient_id INTEGER  NOT NULL,
    amount       INTEGER  NOT NULL CHECK (amount IN (-1, 1)),
    timestamp    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (granter_id) REFERENCES entities (entity_id),
    FOREIGN KEY (recipient_id) REFERENCES entities (entity_id)
);

-- 'UNIQUE' keyword automatically creates indices on 'entities.name' and 'entities.user_id'